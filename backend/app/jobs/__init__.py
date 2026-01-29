"""Data ingestion jobs for Tá na Mão."""

from app.jobs.ingest_ibge import ingest_ibge_data

__all__ = ["ingest_ibge_data"]
