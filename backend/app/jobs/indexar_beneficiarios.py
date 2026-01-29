"""Indexacao de beneficiarios individuais para consulta por CPF.

Este job processa os CSVs do Portal da Transparencia e indexa cada beneficiario
na tabela `beneficiarios` para permitir consultas individuais por CPF.

Diferente dos outros jobs que agregam por municipio, este armazena dados
individuais com CPF hashificado (para privacidade).

Fonte: https://portaldatransparencia.gov.br/download-de-dados/
- Bolsa Familia: /novo-bolsa-familia/{YYYYMM}
- BPC: /bpc/{YYYYMM}
"""

import asyncio
import csv
import io
import os
import zipfile
from datetime import date, datetime
from typing import Optional, Dict, Iterator
import logging
import codecs

import httpx
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.beneficiario import Beneficiario, hash_cpf, mask_cpf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs
BF_URL = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/novo-bolsa-familia"
BPC_URL = "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/bpc"

# SIAFI to IBGE mapping
SIAFI_MAPPING_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data", "siafi_ibge_mapping.csv"
)


def load_siafi_mapping() -> Dict[str, str]:
    """Carrega mapeamento SIAFI -> IBGE."""
    mapping = {}
    if os.path.exists(SIAFI_MAPPING_FILE):
        with open(SIAFI_MAPPING_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if len(row) >= 5:
                    siafi = row[0].strip()
                    ibge = row[4].strip()
                    if siafi and ibge:
                        mapping[siafi] = ibge
    return mapping


async def download_zip(url: str) -> Optional[bytes]:
    """Download ZIP file."""
    logger.info(f"Downloading: {url}")
    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                logger.info(f"Downloaded {len(response.content):,} bytes")
                return response.content
            else:
                logger.error(f"Download failed: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None


def parse_bolsa_familia_csv(zip_content: bytes, siafi_mapping: Dict[str, str]) -> Iterator[Dict]:
    """Parse Bolsa Familia CSV e retorna iterador de beneficiarios.

    Campos do CSV:
    - MES REFERENCIA
    - MES COMPETENCIA
    - UF
    - CODIGO MUNICIPIO SIAFI
    - NOME MUNICIPIO
    - CPF FAVORECIDO
    - NIS FAVORECIDO
    - NOME FAVORECIDO
    - VALOR PARCELA
    """
    zip_buffer = io.BytesIO(zip_content)

    with zipfile.ZipFile(zip_buffer) as zf:
        csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
        if not csv_files:
            logger.error("No CSV file found in ZIP")
            return

        csv_name = csv_files[0]
        logger.info(f"Processing {csv_name}...")

        with zf.open(csv_name) as csv_file:
            text_stream = codecs.getreader('latin-1')(csv_file)
            reader = csv.reader(text_stream, delimiter=';')
            header = next(reader)

            # Map column indices
            col_map = {}
            for i, col in enumerate(header):
                col_upper = col.upper().strip()
                if 'CPF' in col_upper:
                    col_map['cpf'] = i
                elif 'NIS' in col_upper:
                    col_map['nis'] = i
                elif 'NOME FAVORECIDO' in col_upper or 'NOME_FAVORECIDO' in col_upper:
                    col_map['nome'] = i
                elif 'SIAFI' in col_upper:
                    col_map['siafi'] = i
                elif 'VALOR PARCELA' in col_upper or 'VALOR_PARCELA' in col_upper:
                    col_map['valor'] = i
                elif col_upper == 'UF':
                    col_map['uf'] = i
                elif 'MES REFERENCIA' in col_upper or 'MES_REFERENCIA' in col_upper:
                    col_map['mes_ref'] = i

            logger.info(f"Column mapping: {col_map}")

            if 'cpf' not in col_map:
                logger.error("CPF column not found!")
                return

            row_count = 0
            for row in reader:
                row_count += 1

                try:
                    # Extract CPF
                    cpf = row[col_map['cpf']].strip().replace('.', '').replace('-', '').replace('*', '')
                    if not cpf or len(cpf) < 11:
                        continue

                    # Pad with zeros if needed
                    cpf = cpf.zfill(11)

                    # SIAFI to IBGE
                    ibge_code = None
                    if 'siafi' in col_map:
                        siafi = row[col_map['siafi']].strip()
                        ibge_code = siafi_mapping.get(siafi)
                        if not ibge_code and len(siafi) == 7:
                            ibge_code = siafi

                    # Parse value
                    valor = 0.0
                    if 'valor' in col_map:
                        try:
                            valor_str = row[col_map['valor']].replace('.', '').replace(',', '.')
                            valor = float(valor_str)
                        except:
                            valor = 0.0

                    # Parse reference month
                    mes_ref = None
                    if 'mes_ref' in col_map:
                        mes_str = row[col_map['mes_ref']].strip()
                        if len(mes_str) == 6:  # YYYYMM
                            mes_ref = f"{mes_str[:4]}-{mes_str[4:]}"

                    yield {
                        'cpf': cpf,
                        'nis': row[col_map.get('nis', 0)].strip() if 'nis' in col_map else None,
                        'nome': row[col_map.get('nome', 0)].strip()[:200] if 'nome' in col_map else None,
                        'uf': row[col_map.get('uf', 0)].strip() if 'uf' in col_map else None,
                        'ibge_code': ibge_code,
                        'bf_valor': valor,
                        'bf_parcela_mes': mes_ref,
                        'programa': 'BOLSA_FAMILIA'
                    }

                except Exception as e:
                    if row_count < 10:
                        logger.warning(f"Error parsing row {row_count}: {e}")
                    continue

                if row_count % 1000000 == 0:
                    logger.info(f"Processed {row_count:,} rows...")

            logger.info(f"Total rows: {row_count:,}")


def parse_bpc_csv(zip_content: bytes, siafi_mapping: Dict[str, str]) -> Iterator[Dict]:
    """Parse BPC CSV e retorna iterador de beneficiarios.

    Campos tipicos do CSV BPC (variam por ano):
    - UF
    - CODIGO MUNICIPIO SIAFI
    - NOME MUNICIPIO
    - NIS BENEFICIARIO
    - CPF BENEFICIARIO (pode nao existir)
    - NOME BENEFICIARIO
    - NIS REPRESENTANTE
    - CPF REPRESENTANTE
    - NOME REPRESENTANTE
    - NUMERO BENEFICIO
    - BENEFICIO CONCEDIDO JUDICIALMENTE
    - VALOR PARCELA
    """
    zip_buffer = io.BytesIO(zip_content)

    with zipfile.ZipFile(zip_buffer) as zf:
        csv_files = [f for f in zf.namelist() if f.endswith('.csv')]
        if not csv_files:
            logger.error("No CSV file found in ZIP")
            return

        csv_name = csv_files[0]
        logger.info(f"Processing {csv_name}...")

        with zf.open(csv_name) as csv_file:
            text_stream = codecs.getreader('latin-1')(csv_file)
            reader = csv.reader(text_stream, delimiter=';')
            header = next(reader)

            logger.info(f"Headers: {header[:15]}")

            # Map column indices
            col_map = {}
            for i, col in enumerate(header):
                col_upper = col.upper().strip()
                if 'CPF BENEFICIARIO' in col_upper:
                    col_map['cpf'] = i
                elif 'NIS BENEFICIARIO' in col_upper:
                    col_map['nis'] = i
                elif 'NOME BENEFICIARIO' in col_upper:
                    col_map['nome'] = i
                elif 'SIAFI' in col_upper:
                    col_map['siafi'] = i
                elif 'VALOR PARCELA' in col_upper:
                    col_map['valor'] = i
                elif col_upper == 'UF':
                    col_map['uf'] = i

            logger.info(f"Column mapping: {col_map}")

            # BPC pode nao ter CPF, usa NIS como fallback
            id_col = 'cpf' if 'cpf' in col_map else 'nis'
            if id_col not in col_map:
                logger.error("No CPF or NIS column found!")
                return

            row_count = 0
            for row in reader:
                row_count += 1

                try:
                    # Extract identifier
                    id_value = row[col_map[id_col]].strip().replace('.', '').replace('-', '').replace('*', '')
                    if not id_value:
                        continue

                    # Use NIS as CPF if no CPF available (create synthetic hash)
                    if id_col == 'nis':
                        cpf = f"NIS{id_value.zfill(11)}"[:11]
                    else:
                        cpf = id_value.zfill(11)

                    # SIAFI to IBGE
                    ibge_code = None
                    if 'siafi' in col_map:
                        siafi = row[col_map['siafi']].strip()
                        ibge_code = siafi_mapping.get(siafi)

                    # Parse value
                    valor = 0.0
                    if 'valor' in col_map:
                        try:
                            valor_str = row[col_map['valor']].replace('.', '').replace(',', '.')
                            valor = float(valor_str)
                        except:
                            valor = 0.0

                    yield {
                        'cpf': cpf,
                        'nis': row[col_map.get('nis', 0)].strip() if 'nis' in col_map else None,
                        'nome': row[col_map.get('nome', 0)].strip()[:200] if 'nome' in col_map else None,
                        'uf': row[col_map.get('uf', 0)].strip() if 'uf' in col_map else None,
                        'ibge_code': ibge_code,
                        'bpc_valor': valor,
                        'bpc_tipo': 'BPC',  # Could be parsed from "tipo beneficio" column
                        'programa': 'BPC'
                    }

                except Exception as e:
                    if row_count < 10:
                        logger.warning(f"Error parsing row {row_count}: {e}")
                    continue

                if row_count % 500000 == 0:
                    logger.info(f"Processed {row_count:,} rows...")

            logger.info(f"Total rows: {row_count:,}")


def upsert_beneficiarios(db: Session, beneficiarios: Iterator[Dict], batch_size: int = 10000):
    """Insere ou atualiza beneficiarios em lotes.

    Usa upsert para atualizar se CPF ja existe.
    """
    batch = []
    total_inserted = 0
    total_updated = 0

    for ben in beneficiarios:
        cpf = ben['cpf']
        cpf_hashed = hash_cpf(cpf)
        cpf_masked = mask_cpf(cpf)

        record = {
            'cpf_hash': cpf_hashed,
            'cpf_masked': cpf_masked,
            'nis': ben.get('nis'),
            'nome': ben.get('nome'),
            'uf': ben.get('uf'),
            'ibge_code': ben.get('ibge_code'),
            'atualizado_em': datetime.utcnow(),
            'fonte': 'PORTAL_TRANSPARENCIA'
        }

        # Set program-specific fields
        if ben.get('programa') == 'BOLSA_FAMILIA':
            record['bf_ativo'] = True
            record['bf_valor'] = ben.get('bf_valor')
            record['bf_parcela_mes'] = ben.get('bf_parcela_mes')
            record['bf_data_referencia'] = date.today()
        elif ben.get('programa') == 'BPC':
            record['bpc_ativo'] = True
            record['bpc_valor'] = ben.get('bpc_valor')
            record['bpc_tipo'] = ben.get('bpc_tipo')
            record['bpc_data_referencia'] = date.today()

        batch.append(record)

        if len(batch) >= batch_size:
            inserted, updated = _execute_upsert(db, batch)
            total_inserted += inserted
            total_updated += updated
            batch = []
            logger.info(f"Progress: {total_inserted + total_updated:,} records processed")

    # Final batch
    if batch:
        inserted, updated = _execute_upsert(db, batch)
        total_inserted += inserted
        total_updated += updated

    logger.info(f"Total: {total_inserted:,} inserted, {total_updated:,} updated")
    return total_inserted, total_updated


def _execute_upsert(db: Session, records: list) -> tuple:
    """Execute upsert for a batch of records."""
    if not records:
        return 0, 0

    stmt = insert(Beneficiario).values(records)

    # On conflict, update relevant fields
    update_dict = {
        'nome': stmt.excluded.nome,
        'uf': stmt.excluded.uf,
        'ibge_code': stmt.excluded.ibge_code,
        'atualizado_em': stmt.excluded.atualizado_em,
    }

    # Update program-specific fields based on what's being inserted
    if records[0].get('bf_ativo'):
        update_dict.update({
            'bf_ativo': stmt.excluded.bf_ativo,
            'bf_valor': stmt.excluded.bf_valor,
            'bf_parcela_mes': stmt.excluded.bf_parcela_mes,
            'bf_data_referencia': stmt.excluded.bf_data_referencia,
        })
    if records[0].get('bpc_ativo'):
        update_dict.update({
            'bpc_ativo': stmt.excluded.bpc_ativo,
            'bpc_valor': stmt.excluded.bpc_valor,
            'bpc_tipo': stmt.excluded.bpc_tipo,
            'bpc_data_referencia': stmt.excluded.bpc_data_referencia,
        })

    upsert_stmt = stmt.on_conflict_do_update(
        index_elements=['cpf_hash'],
        set_=update_dict
    )

    try:
        db.execute(upsert_stmt)
        db.commit()
        # PostgreSQL doesn't easily tell us inserted vs updated, so we estimate
        return len(records), 0
    except Exception as e:
        logger.error(f"Upsert error: {e}")
        db.rollback()
        return 0, 0


async def indexar_bolsa_familia(year: int, month: int):
    """Indexa beneficiarios do Bolsa Familia de um mes.

    Args:
        year: Ano (ex: 2024)
        month: Mes (1-12)
    """
    period = f"{year}{month:02d}"
    url = f"{BF_URL}/{period}_NovoBolsaFamilia.zip"

    logger.info(f"=== Indexando Bolsa Familia {period} ===")

    # Download
    zip_content = await download_zip(url)
    if not zip_content:
        logger.error("Failed to download")
        return

    # Load SIAFI mapping
    siafi_mapping = load_siafi_mapping()

    # Parse and insert
    db = SessionLocal()
    try:
        beneficiarios = parse_bolsa_familia_csv(zip_content, siafi_mapping)
        inserted, updated = upsert_beneficiarios(db, beneficiarios)
        logger.info(f"=== Concluido: {inserted + updated:,} beneficiarios indexados ===")
    finally:
        db.close()


async def indexar_bpc(year: int, month: int):
    """Indexa beneficiarios do BPC de um mes.

    Args:
        year: Ano (ex: 2024)
        month: Mes (1-12)
    """
    period = f"{year}{month:02d}"
    url = f"{BPC_URL}/{period}_BPC.zip"

    logger.info(f"=== Indexando BPC {period} ===")

    # Download
    zip_content = await download_zip(url)
    if not zip_content:
        logger.error("Failed to download")
        return

    # Load SIAFI mapping
    siafi_mapping = load_siafi_mapping()

    # Parse and insert
    db = SessionLocal()
    try:
        beneficiarios = parse_bpc_csv(zip_content, siafi_mapping)
        inserted, updated = upsert_beneficiarios(db, beneficiarios)
        logger.info(f"=== Concluido: {inserted + updated:,} beneficiarios indexados ===")
    finally:
        db.close()


def consultar_por_cpf(cpf: str) -> Optional[Dict]:
    """Consulta beneficiario por CPF.

    Args:
        cpf: CPF (com ou sem formatacao)

    Returns:
        Dict com dados do beneficiario ou None
    """
    db = SessionLocal()
    try:
        beneficiario = Beneficiario.buscar_por_cpf(db, cpf)
        if beneficiario:
            return beneficiario.to_dict()
        return None
    finally:
        db.close()


# CLI
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Uso:")
        print("  python -m app.jobs.indexar_beneficiarios bf 2024 10")
        print("  python -m app.jobs.indexar_beneficiarios bpc 2024 10")
        print("  python -m app.jobs.indexar_beneficiarios consultar 12345678900")
        sys.exit(1)

    comando = sys.argv[1].lower()

    if comando == "bf":
        year = int(sys.argv[2])
        month = int(sys.argv[3])
        asyncio.run(indexar_bolsa_familia(year, month))

    elif comando == "bpc":
        year = int(sys.argv[2])
        month = int(sys.argv[3])
        asyncio.run(indexar_bpc(year, month))

    elif comando == "consultar":
        cpf = sys.argv[2]
        resultado = consultar_por_cpf(cpf)
        if resultado:
            import json
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        else:
            print(f"CPF {cpf} nao encontrado")

    else:
        print(f"Comando desconhecido: {comando}")
        sys.exit(1)
