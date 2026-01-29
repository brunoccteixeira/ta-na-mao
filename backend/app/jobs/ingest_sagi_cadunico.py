"""CadÚnico data extraction from SAGI RI.

This script extracts CadÚnico data from the SAGI Relatório de Informações (RI).
It supports multiple methods:
1. Direct HTTP POST (faster, but data may not always load)
2. Playwright browser automation (slower, but more reliable)

Source: https://aplicacoes.mds.gov.br/sagi/ri/relatorios/cidadania/

Usage:
    # Test with one municipality (HTTP method)
    python -m app.jobs.ingest_sagi_cadunico --test 3550308

    # Run for all municipalities
    python -m app.jobs.ingest_sagi_cadunico

    # Run for a specific state
    python -m app.jobs.ingest_sagi_cadunico --state SP

    # Use Playwright (browser automation) instead of HTTP
    python -m app.jobs.ingest_sagi_cadunico --browser
"""

import asyncio
import re
import logging
from datetime import date
from typing import Optional
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Municipality, CadUnicoData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SAGI RI URLs
RI_BASE_URL = "https://aplicacoes.mds.gov.br/sagi/ri/relatorios/cidadania/"
CADUNICO_MODULE = "cadastro-unico.php"

# Default delay between requests (seconds)
REQUEST_DELAY = 1.0


@dataclass
class CadUnicoExtract:
    """Extracted CadÚnico data from SAGI."""
    total_families: int = 0
    total_persons: int = 0
    families_extreme_poverty: int = 0
    families_poverty: int = 0
    families_low_income: int = 0
    persons_0_5: int = 0
    persons_6_14: int = 0
    persons_15_17: int = 0
    persons_18_64: int = 0
    persons_65_plus: int = 0
    reference_date: str = ""


def parse_brazilian_number(text: str) -> int:
    """Parse Brazilian formatted number (1.234.567) to int."""
    if not text or text == '-':
        return 0
    # Remove dots and commas, keep only digits
    clean = re.sub(r'[^\d]', '', text)
    try:
        return int(clean) if clean else 0
    except ValueError:
        return 0


def parse_cadunico_html(html: str) -> CadUnicoExtract:
    """Parse CadÚnico data from RI module HTML.

    The HTML structure has:
    - .dado_textoc elements with the values
    - .titulo_textoc with labels like "FAMÍLIAS", "PESSOAS"
    - .ref_textoc with context like "em situação de pobreza"
    """
    soup = BeautifulSoup(html, 'html.parser')
    data = CadUnicoExtract()

    # Find all containers with data
    containers = soup.find_all(class_='container_prog')

    for container in containers:
        titulo = container.find(class_='titulo_textoc')
        ref = container.find(class_='ref_textoc')
        dado = container.find(class_='dado_textoc')

        if not dado:
            continue

        value = parse_brazilian_number(dado.get_text(strip=True))
        if value == 0:
            continue

        titulo_text = titulo.get_text(strip=True).lower() if titulo else ''
        ref_text = ref.get_text(strip=True).lower() if ref else ''

        # Classify based on labels
        if 'família' in titulo_text:
            if 'cadastr' in titulo_text:  # "Famílias Cadastradas"
                data.total_families = value
            elif 'extrema' in ref_text or 'extrema' in titulo_text:
                data.families_extreme_poverty = value
            elif 'pobreza' in ref_text:
                data.families_poverty = value
            elif 'baixa renda' in ref_text:
                data.families_low_income = value
            elif 'acima' in ref_text or '½' in ref_text:
                pass  # Above threshold, not tracked

        elif 'pessoa' in titulo_text:
            if 'cadastr' in titulo_text:  # "Pessoas Cadastradas"
                data.total_persons = value
            elif 'extrema' in ref_text or 'extrema' in titulo_text:
                pass  # persons extreme poverty
            elif 'pobreza' in ref_text:
                pass  # persons poverty
            elif 'baixa renda' in ref_text:
                pass  # persons low income

    # Try to find reference date
    refs = soup.find_all(class_='ref_textoc')
    for r in refs:
        text = r.get_text(strip=True)
        # Look for date patterns like "Ref: out/2024" or "Cadastro Único - out/2024"
        match = re.search(r'(\w+)/(\d{4})', text)
        if match:
            data.reference_date = f"{match.group(1)}/{match.group(2)}"
            break

    return data


async def fetch_cadunico_http(
    client: httpx.AsyncClient,
    ibge_code: str,
    periodo: str = None
) -> Optional[CadUnicoExtract]:
    """Fetch CadÚnico data via HTTP POST.

    This method is faster but may return empty data if the server
    requires JavaScript rendering.
    """
    url = RI_BASE_URL + CADUNICO_MODULE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': f'{RI_BASE_URL}?codigo={ibge_code}',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = {
        'codigo': ibge_code,
        'p_ibge': ibge_code,
        'ibge': ibge_code,
        'area_especial': '',
        'area': '',
        'mes': '',
        'ano': '',
        'usa': '',
        'rcr': '',
        'rpp': '',
        'fa': '0',
        'e': '1',  # Show state comparison
        'r': '1',  # Show region comparison
        'b': '1',  # Show Brazil comparison
    }

    if periodo:
        # periodo format: 2024-10-01 or 10-2024
        if '-' in periodo:
            parts = periodo.split('-')
            if len(parts[0]) == 4:  # 2024-10-01
                data['ano'] = parts[0]
                data['mes'] = parts[1]
                data['periodo'] = periodo
            else:  # 10-2024
                data['mes'] = parts[0]
                data['ano'] = parts[1]

    try:
        # First establish session
        await client.get(f'{RI_BASE_URL}?codigo={ibge_code}', headers=headers)

        # Then request module
        response = await client.post(url, data=data, headers=headers)

        if response.status_code == 200:
            return parse_cadunico_html(response.text)
        else:
            logger.warning(f"HTTP {response.status_code} for {ibge_code}")
            return None

    except Exception as e:
        logger.error(f"HTTP error for {ibge_code}: {e}")
        return None


class BrowserManager:
    """Manages a reusable Playwright browser instance."""

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self._lock = asyncio.Lock()
        self.request_count = 0
        self.max_requests_before_restart = 50  # Restart browser periodically

    async def start(self):
        """Start the browser."""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.request_count = 0
        logger.info("Browser started")

    async def stop(self):
        """Stop the browser."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.browser = None
        self.context = None
        self.playwright = None
        logger.info("Browser stopped")

    async def restart_if_needed(self):
        """Restart browser if it has been used too many times."""
        if self.request_count >= self.max_requests_before_restart:
            logger.info(f"Restarting browser after {self.request_count} requests...")
            await self.stop()
            await asyncio.sleep(1)
            await self.start()

    async def get_page(self):
        """Get a new page from the browser."""
        async with self._lock:
            await self.restart_if_needed()
            if not self.browser:
                await self.start()
            self.request_count += 1
            return await self.context.new_page()


# Global browser manager for reuse
_browser_manager: Optional[BrowserManager] = None


async def get_browser_manager() -> BrowserManager:
    """Get or create the global browser manager."""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
        await _browser_manager.start()
    return _browser_manager


async def fetch_cadunico_browser(
    ibge_code: str,
    periodo: str = None,
    browser_manager: BrowserManager = None,
    max_retries: int = 2
) -> Optional[CadUnicoExtract]:
    """Fetch CadÚnico data using Playwright browser automation.

    This method is slower but more reliable as it renders JavaScript.
    Uses a shared browser instance for better performance.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.error("Playwright not installed. Install with: pip install playwright && playwright install chromium")
        return None

    if browser_manager is None:
        browser_manager = await get_browser_manager()

    for attempt in range(max_retries + 1):
        page = None
        try:
            page = await browser_manager.get_page()

            # Build URL
            url = f'{RI_BASE_URL}?codigo={ibge_code}'
            if periodo:
                url += f'&periodo={periodo}'

            # Use 'load' instead of 'networkidle' - faster and more reliable
            await page.goto(url, wait_until='load', timeout=45000)

            # Wait for CadÚnico module to load (with shorter timeout)
            try:
                await page.wait_for_selector('#cadastrounico', timeout=15000)
            except:
                logger.debug(f"CadÚnico selector not found for {ibge_code}, checking anyway...")

            # Wait for AJAX data to load (check for actual values)
            await asyncio.sleep(3)

            # Try to wait for actual data values
            try:
                await page.wait_for_function(
                    """() => {
                        const dados = document.querySelectorAll('.dado_textoc');
                        for (let d of dados) {
                            const text = d.textContent.trim();
                            if (text && text !== '-' && /\\d/.test(text)) {
                                return true;
                            }
                        }
                        return false;
                    }""",
                    timeout=10000
                )
            except:
                logger.debug(f"Data values not detected for {ibge_code}")

            html = await page.content()
            await page.close()

            # Find the cadastro-unico module section
            soup = BeautifulSoup(html, 'html.parser')
            cadunico_section = soup.find(id='cadastrounico')

            if cadunico_section:
                # Get parent div with all module content
                module_div = cadunico_section.find_parent(class_='dvOMR')
                if module_div:
                    return parse_cadunico_html(str(module_div))

            return parse_cadunico_html(html)

        except Exception as e:
            if page:
                try:
                    await page.close()
                except:
                    pass

            if attempt < max_retries:
                logger.warning(f"Retry {attempt + 1}/{max_retries} for {ibge_code}: {e}")
                await asyncio.sleep(2)
            else:
                logger.error(f"Browser error for {ibge_code} after {max_retries + 1} attempts: {e}")
                return None

    return None


def save_cadunico_data(
    db: Session,
    municipality_id: int,
    data: CadUnicoExtract,
    reference_date: date
) -> bool:
    """Save extracted CadÚnico data to database."""
    try:
        # Check if record exists
        existing = db.query(CadUnicoData).filter(
            CadUnicoData.municipality_id == municipality_id,
            CadUnicoData.reference_date == reference_date
        ).first()

        if existing:
            existing.total_families = data.total_families
            existing.total_persons = data.total_persons
            existing.families_extreme_poverty = data.families_extreme_poverty
            existing.families_poverty = data.families_poverty
            existing.families_low_income = data.families_low_income
            existing.persons_0_5_years = data.persons_0_5
            existing.persons_6_14_years = data.persons_6_14
            existing.persons_15_17_years = data.persons_15_17
            existing.persons_18_64_years = data.persons_18_64
            existing.persons_65_plus = data.persons_65_plus
            logger.debug(f"Updated CadÚnico for municipality {municipality_id}")
        else:
            cadunico = CadUnicoData(
                municipality_id=municipality_id,
                reference_date=reference_date,
                total_families=data.total_families,
                total_persons=data.total_persons,
                families_extreme_poverty=data.families_extreme_poverty,
                families_poverty=data.families_poverty,
                families_low_income=data.families_low_income,
                persons_0_5_years=data.persons_0_5,
                persons_6_14_years=data.persons_6_14,
                persons_15_17_years=data.persons_15_17,
                persons_18_64_years=data.persons_18_64,
                persons_65_plus=data.persons_65_plus,
            )
            db.add(cadunico)
            logger.debug(f"Created CadÚnico for municipality {municipality_id}")

        db.commit()
        return True

    except Exception as e:
        logger.error(f"Error saving CadÚnico: {e}")
        db.rollback()
        return False


def get_fresh_db_session():
    """Get a fresh database session, closing any existing one."""
    return SessionLocal()


async def ingest_all_municipalities(
    state_filter: str = None,
    periodo: str = None,
    use_browser: bool = False,
    delay: float = REQUEST_DELAY,
    batch_size: int = 50
):
    """Ingest CadÚnico data for all municipalities.

    Args:
        state_filter: Filter by state abbreviation (e.g., 'SP')
        periodo: Reference period (e.g., '2024-10-01')
        use_browser: Use Playwright browser automation (required for SAGI)
        delay: Delay between requests in seconds
        batch_size: Number of municipalities to process before refreshing DB connection
    """
    global _browser_manager

    logger.info("=" * 60)
    logger.info("SAGI CadÚnico Data Ingestion")
    logger.info(f"Method: {'Browser (Playwright)' if use_browser else 'HTTP'}")
    logger.info(f"Batch size: {batch_size}")
    logger.info("=" * 60)

    # Get municipalities list (quick query)
    db = get_fresh_db_session()
    try:
        query = db.query(Municipality)
        if state_filter:
            from app.models import State
            state = db.query(State).filter(State.abbreviation == state_filter.upper()).first()
            if state:
                query = query.filter(Municipality.state_id == state.id)
                logger.info(f"Filtering by state: {state.name}")
            else:
                logger.error(f"State not found: {state_filter}")
                return

        # Get list of (id, ibge_code, name) tuples to avoid keeping ORM objects
        municipalities = [(m.id, m.ibge_code, m.name) for m in query.order_by(Municipality.ibge_code).all()]
        total = len(municipalities)
    finally:
        db.close()

    logger.info(f"Processing {total} municipalities...")
    if use_browser:
        logger.info(f"Estimated time: {(total * 8) / 60:.1f} minutes (with shared browser)")
    else:
        logger.info(f"Estimated time: {(total * delay) / 60:.1f} minutes")
    logger.info("=" * 60)

    success_count = 0
    error_count = 0
    empty_count = 0

    # Initialize browser manager for browser mode
    browser_manager = None
    if use_browser:
        browser_manager = BrowserManager()
        await browser_manager.start()

    # Create HTTP client for non-browser mode
    client = httpx.AsyncClient(timeout=30.0, follow_redirects=True) if not use_browser else None

    try:
        # Process in batches to avoid DB connection timeout
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch = municipalities[batch_start:batch_end]

            logger.info(f"Processing batch {batch_start + 1}-{batch_end} of {total}...")

            # Get fresh DB connection for each batch
            db = get_fresh_db_session()

            try:
                for i, (muni_id, ibge_code, name) in enumerate(batch, batch_start + 1):
                    try:
                        # Fetch data
                        if use_browser:
                            data = await fetch_cadunico_browser(ibge_code, periodo, browser_manager)
                        else:
                            data = await fetch_cadunico_http(client, ibge_code, periodo)

                        if not data:
                            logger.warning(f"No data for {name}")
                            error_count += 1
                            continue

                        if data.total_families == 0 and data.total_persons == 0:
                            logger.debug(f"Empty data for {name}")
                            empty_count += 1
                            continue

                        # Determine reference date
                        ref_date = date.today().replace(day=1)
                        if periodo:
                            parts = periodo.split('-')
                            if len(parts) >= 2:
                                if len(parts[0]) == 4:  # 2024-10-01
                                    ref_date = date(int(parts[0]), int(parts[1]), 1)
                                else:  # 10-2024
                                    ref_date = date(int(parts[1]), int(parts[0]), 1)

                        # Save
                        if save_cadunico_data(db, muni_id, data, ref_date):
                            success_count += 1
                            logger.info(
                                f"[{i}/{total}] {name}: "
                                f"{data.total_families:,} families, "
                                f"{data.total_persons:,} persons"
                            )

                        # Progress log
                        if i % 100 == 0:
                            logger.info(
                                f"Progress: {i}/{total} "
                                f"({success_count} success, {empty_count} empty, {error_count} errors)"
                            )

                        await asyncio.sleep(delay)

                    except Exception as e:
                        logger.error(f"Error processing {name}: {e}")
                        error_count += 1

            finally:
                # Close DB connection after each batch
                try:
                    db.close()
                except Exception as e:
                    logger.warning(f"Error closing DB: {e}")

            # Small delay between batches
            await asyncio.sleep(1)

    finally:
        # Cleanup
        if client:
            await client.aclose()

        if browser_manager:
            await browser_manager.stop()
            _browser_manager = None

    logger.info("=" * 60)
    logger.info("INGESTION COMPLETE")
    logger.info(f"Success: {success_count}")
    logger.info(f"Empty (no data): {empty_count}")
    logger.info(f"Errors: {error_count}")
    logger.info("=" * 60)


async def test_municipality(ibge_code: str, periodo: str = None, use_browser: bool = False):
    """Test extraction for a single municipality."""
    global _browser_manager

    logger.info(f"Testing {ibge_code} with {'browser' if use_browser else 'HTTP'}")

    browser_manager = None
    try:
        if use_browser:
            browser_manager = BrowserManager()
            await browser_manager.start()
            data = await fetch_cadunico_browser(ibge_code, periodo, browser_manager)
        else:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                data = await fetch_cadunico_http(client, ibge_code, periodo)

        if data:
            logger.info("Extracted data:")
            logger.info(f"  Total families: {data.total_families:,}")
            logger.info(f"  Total persons: {data.total_persons:,}")
            logger.info(f"  Extreme poverty: {data.families_extreme_poverty:,}")
            logger.info(f"  Poverty: {data.families_poverty:,}")
            logger.info(f"  Low income: {data.families_low_income:,}")
            logger.info(f"  Reference: {data.reference_date}")

            if data.total_families == 0:
                logger.warning("Data is empty - HTTP method may not work for this server")
                logger.warning("Try running with --browser flag to use Playwright")
        else:
            logger.error("No data extracted")

    finally:
        if browser_manager:
            await browser_manager.stop()
        _browser_manager = None


def run_ingestion():
    """Synchronous wrapper for full ingestion."""
    asyncio.run(ingest_all_municipalities())


if __name__ == "__main__":
    import sys

    use_browser = '--browser' in sys.argv

    # Remove --browser from args for further processing
    args = [a for a in sys.argv if a != '--browser']

    if len(args) > 1:
        if args[1] == "--test" and len(args) > 2:
            ibge_code = args[2]
            periodo = args[3] if len(args) > 3 else None
            asyncio.run(test_municipality(ibge_code, periodo, use_browser))

        elif args[1] == "--state" and len(args) > 2:
            state = args[2]
            periodo = args[3] if len(args) > 3 else None
            asyncio.run(ingest_all_municipalities(state_filter=state, periodo=periodo, use_browser=use_browser))

        elif args[1] == "--help":
            print(__doc__)
        else:
            print("Unknown option. Use --help for usage info.")
    else:
        asyncio.run(ingest_all_municipalities(use_browser=use_browser))
