#!/usr/bin/env python3
"""
URL Validator for Tá na Mão benefits catalog.
Checks all sourceUrls are accessible (HTTP HEAD/GET).

Usage:
    python scripts/validate_urls.py
    python scripts/validate_urls.py --scope federal
    python scripts/validate_urls.py --scope sectoral
    python scripts/validate_urls.py --scope state
    python scripts/validate_urls.py --scope municipal
    python scripts/validate_urls.py --json  # Output JSON report
"""

import argparse
import asyncio
import json
import glob
import os
import sys
import time
from pathlib import Path
from dataclasses import dataclass, asdict

# Try aiohttp first (faster), fall back to urllib
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    import urllib.request
    import urllib.error
    import ssl

BASE_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "data" / "benefits"

# Concurrency limits
MAX_CONCURRENT = 10
DELAY_BETWEEN_MS = 100
TIMEOUT_SECONDS = 10
MAX_REDIRECTS = 3


@dataclass
class UrlResult:
    benefit_id: str
    scope: str
    url: str
    status: int  # 0 = error, -1 = timeout, -2 = dns error
    response_time_ms: int
    final_url: str
    error: str = ""


def load_benefits(scope_filter: str = "") -> list[dict]:
    """Load benefits, optionally filtered by scope."""
    benefits = []

    if not scope_filter or scope_filter == "federal":
        fp = BASE_DIR / "federal.json"
        if fp.exists():
            with open(fp, encoding="utf-8") as f:
                for b in json.load(f)["benefits"]:
                    b["_scope"] = "federal"
                    benefits.append(b)

    if not scope_filter or scope_filter == "sectoral":
        fp = BASE_DIR / "sectoral.json"
        if fp.exists():
            with open(fp, encoding="utf-8") as f:
                for b in json.load(f)["benefits"]:
                    b["_scope"] = "sectoral"
                    benefits.append(b)

    if not scope_filter or scope_filter == "state":
        for fp in sorted(glob.glob(str(BASE_DIR / "states" / "*.json"))):
            with open(fp, encoding="utf-8") as f:
                for b in json.load(f)["benefits"]:
                    b["_scope"] = "state"
                    benefits.append(b)

    if not scope_filter or scope_filter == "municipal":
        for fp in sorted(glob.glob(str(BASE_DIR / "municipalities" / "*.json"))):
            with open(fp, encoding="utf-8") as f:
                data = json.load(f)
                for b in data.get("benefits", []):
                    b["_scope"] = "municipal"
                    benefits.append(b)

    return benefits


async def check_url_aiohttp(session: aiohttp.ClientSession, benefit: dict, semaphore: asyncio.Semaphore) -> UrlResult:
    """Check a single URL using aiohttp."""
    bid = benefit.get("id", "UNKNOWN")
    scope = benefit.get("_scope", "unknown")
    url = benefit.get("sourceUrl", "")

    if not url:
        return UrlResult(bid, scope, "", 0, 0, "", "No sourceUrl")

    async with semaphore:
        await asyncio.sleep(DELAY_BETWEEN_MS / 1000)
        start = time.monotonic()
        try:
            async with session.head(
                url,
                timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
                allow_redirects=True,
                max_redirects=MAX_REDIRECTS,
            ) as resp:
                elapsed = int((time.monotonic() - start) * 1000)
                return UrlResult(bid, scope, url, resp.status, elapsed, str(resp.url))
        except asyncio.TimeoutError:
            elapsed = int((time.monotonic() - start) * 1000)
            return UrlResult(bid, scope, url, -1, elapsed, "", "Timeout")
        except aiohttp.ClientError as e:
            elapsed = int((time.monotonic() - start) * 1000)
            # Try GET as fallback (some servers reject HEAD)
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS),
                    allow_redirects=True,
                    max_redirects=MAX_REDIRECTS,
                ) as resp:
                    elapsed = int((time.monotonic() - start) * 1000)
                    return UrlResult(bid, scope, url, resp.status, elapsed, str(resp.url))
            except Exception as e2:
                elapsed = int((time.monotonic() - start) * 1000)
                return UrlResult(bid, scope, url, 0, elapsed, "", str(e2)[:200])
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            return UrlResult(bid, scope, url, 0, elapsed, "", str(e)[:200])


async def run_aiohttp(benefits: list[dict]) -> list[UrlResult]:
    """Run URL checks using aiohttp."""
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    headers = {
        "User-Agent": "TaNaMao-URLValidator/1.0 (benefit-catalog-audit)"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = [check_url_aiohttp(session, b, semaphore) for b in benefits]
        return await asyncio.gather(*tasks)


def check_url_urllib(benefit: dict) -> UrlResult:
    """Fallback: check a URL using urllib (synchronous)."""
    bid = benefit.get("id", "UNKNOWN")
    scope = benefit.get("_scope", "unknown")
    url = benefit.get("sourceUrl", "")

    if not url:
        return UrlResult(bid, scope, "", 0, 0, "", "No sourceUrl")

    ctx = ssl.create_default_context()
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "TaNaMao-URLValidator/1.0"
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS, context=ctx) as resp:
            elapsed = int((time.monotonic() - start) * 1000)
            return UrlResult(bid, scope, url, resp.status, elapsed, resp.url)
    except urllib.error.HTTPError as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return UrlResult(bid, scope, url, e.code, elapsed, url, str(e.reason))
    except urllib.error.URLError as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return UrlResult(bid, scope, url, 0, elapsed, "", str(e.reason)[:200])
    except TimeoutError:
        elapsed = int((time.monotonic() - start) * 1000)
        return UrlResult(bid, scope, url, -1, elapsed, "", "Timeout")
    except Exception as e:
        elapsed = int((time.monotonic() - start) * 1000)
        return UrlResult(bid, scope, url, 0, elapsed, "", str(e)[:200])


def run_urllib(benefits: list[dict]) -> list[UrlResult]:
    """Run URL checks using urllib (sequential fallback)."""
    results = []
    for b in benefits:
        results.append(check_url_urllib(b))
        time.sleep(DELAY_BETWEEN_MS / 1000)
    return results


def print_report(results: list[UrlResult]):
    """Print human-readable report."""
    total = len(results)
    ok = [r for r in results if 200 <= r.status <= 399]
    redirects = [r for r in results if 300 <= r.status <= 399]
    not_found = [r for r in results if r.status == 404]
    server_errors = [r for r in results if 500 <= r.status <= 599]
    timeouts = [r for r in results if r.status == -1]
    errors = [r for r in results if r.status <= 0 and r.status != -1]
    no_url = [r for r in results if not r.url]

    print(f"\n{'=' * 70}")
    print(f"URL VALIDATION REPORT")
    print(f"{'=' * 70}")
    print(f"  Total checked: {total}")
    print(f"  OK (2xx):      {len(ok)} ({len(ok)*100//max(total,1)}%)")
    print(f"  Redirects:     {len(redirects)}")
    print(f"  Not Found:     {len(not_found)}")
    print(f"  Server Error:  {len(server_errors)}")
    print(f"  Timeout:       {len(timeouts)}")
    print(f"  Other Error:   {len(errors)}")
    print(f"  No URL:        {len(no_url)}")

    # Scope breakdown
    scopes = set(r.scope for r in results)
    print(f"\nBy scope:")
    for scope in sorted(scopes):
        scope_results = [r for r in results if r.scope == scope]
        scope_ok = [r for r in scope_results if 200 <= r.status <= 399]
        print(f"  {scope}: {len(scope_ok)}/{len(scope_results)} OK")

    # Average response time
    valid_times = [r.response_time_ms for r in results if r.status > 0]
    if valid_times:
        avg = sum(valid_times) // len(valid_times)
        print(f"\nAvg response time: {avg}ms (of {len(valid_times)} successful)")

    # Problem URLs
    problems = [r for r in results if r.status < 200 or r.status >= 400]
    if problems:
        print(f"\n{'=' * 70}")
        print(f"PROBLEM URLs ({len(problems)}):")
        print(f"{'=' * 70}")
        for r in sorted(problems, key=lambda x: (x.status, x.benefit_id)):
            status_label = {
                -1: "TIMEOUT",
                -2: "DNS_ERR",
                0: "ERROR",
                404: "NOT_FOUND",
                403: "FORBIDDEN",
                500: "SERVER_ERR",
                502: "BAD_GW",
                503: "UNAVAIL",
            }.get(r.status, f"HTTP_{r.status}")
            print(f"  [{status_label}] {r.benefit_id}: {r.url}")
            if r.error:
                print(f"           Error: {r.error[:100]}")

    if not problems:
        print(f"\n  ✅ All URLs are accessible!")


def main():
    parser = argparse.ArgumentParser(description="Validate sourceUrls in benefit catalog")
    parser.add_argument("--scope", choices=["federal", "sectoral", "state", "municipal"], help="Filter by scope")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--dry-run", action="store_true", help="List URLs without checking")
    args = parser.parse_args()

    benefits = load_benefits(args.scope or "")
    # Deduplicate by URL
    seen_urls = set()
    unique_benefits = []
    for b in benefits:
        url = b.get("sourceUrl", "")
        if url not in seen_urls:
            seen_urls.add(url)
            unique_benefits.append(b)
        else:
            # Keep all for reporting but only check unique URLs
            unique_benefits.append(b)

    print(f"Loaded {len(benefits)} benefits ({len(seen_urls)} unique URLs)")
    if args.scope:
        print(f"Scope filter: {args.scope}")

    if args.dry_run:
        for b in benefits:
            print(f"  {b.get('id', '?')}: {b.get('sourceUrl', 'NO URL')}")
        return

    print(f"\nChecking URLs (max {MAX_CONCURRENT} concurrent, {TIMEOUT_SECONDS}s timeout)...")
    start = time.monotonic()

    if HAS_AIOHTTP:
        print("Using aiohttp (async)")
        results = asyncio.run(run_aiohttp(benefits))
    else:
        print("Using urllib (sync fallback — install aiohttp for speed)")
        results = run_urllib(benefits)

    elapsed = time.monotonic() - start
    print(f"Completed in {elapsed:.1f}s")

    print_report(results)

    if args.json:
        report = {
            "total": len(results),
            "scope": args.scope or "all",
            "results": [asdict(r) for r in results],
        }
        report_path = BASE_DIR / "url-validation-report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\nJSON report saved to: {report_path}")

    # Exit code: 1 if any 404s
    not_found = [r for r in results if r.status == 404]
    if not_found:
        sys.exit(1)


if __name__ == "__main__":
    main()
