"""Load Zomato dataset from Hugging Face and cache as Parquet."""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

import pandas as pd
from datasets import load_dataset

from src.config import Settings, get_settings
from src.data.preprocessor import log_dataset_stats, preprocess_dataframe
from src.domain.exceptions import DataLoadError, DataValidationError

logger = logging.getLogger(__name__)

RAW_COLUMN_MAP = {
    "name": "name",
    "address": "address",
    "location": "location",
    "rate": "rate",
    "votes": "votes",
    "cuisines": "cuisines",
    "approx_cost(for two people)": "cost",
    "url": "url",
    "rest_type": "rest_type",
    "listed_in(city)": "listed_in_city",
}


def _configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_raw_dataset(dataset_id: str | None = None) -> pd.DataFrame:
    """Download dataset from Hugging Face and return as pandas DataFrame."""
    settings = get_settings()
    dataset_id = dataset_id or settings.hf_dataset_id

    max_retries = 3
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                "Loading dataset '%s' from Hugging Face (attempt %d/%d)...",
                dataset_id,
                attempt,
                max_retries,
            )
            ds = load_dataset(dataset_id, split="train")
            df = ds.to_pandas()
            logger.info("Downloaded %d raw rows", len(df))
            return df
        except Exception as exc:
            last_error = exc
            logger.warning("Download failed: %s", exc)
            if attempt < max_retries:
                wait = 2**attempt
                logger.info("Retrying in %d seconds...", wait)
                time.sleep(wait)

    raise DataLoadError(
        f"Failed to load dataset '{dataset_id}' after {max_retries} attempts: {last_error}"
    ) from last_error


def _atomic_write_parquet(df: pd.DataFrame, path: Path) -> None:
    """Write parquet atomically via temp file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(".parquet.tmp")

    try:
        df.to_parquet(tmp_path, index=False)
        tmp_path.replace(path)
        logger.info("Wrote cache to %s", path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def ingest_dataset(
    settings: Settings | None = None,
    *,
    force: bool = False,
    skip_download: bool = False,
) -> pd.DataFrame:
    """
    Run full ingestion pipeline: load (or skip), preprocess, cache.

    If cache exists and force=False, returns cached data without re-downloading.
    """
    settings = settings or get_settings()
    cache_path = settings.data_cache_path

    if cache_path.exists() and not force and not skip_download:
        logger.info("Cache hit: loading from %s", cache_path)
        df = pd.read_parquet(cache_path)
        log_dataset_stats(df)
        return df

    if skip_download and not cache_path.exists():
        raise DataLoadError(
            f"No cache at {cache_path}. Run ingest without --skip-download first."
        )

    if cache_path.exists() and force:
        logger.info("Force re-ingest: ignoring existing cache")

    raw_df: pd.DataFrame
    if skip_download:
        raw_df = pd.read_parquet(cache_path)
        logger.info("Loaded %d rows from cache for re-processing", len(raw_df))
    else:
        raw_df = load_raw_dataset(settings.hf_dataset_id)

    processed = preprocess_dataframe(raw_df)

    if len(processed) < 1000:
        logger.warning(
            "Processed dataset has only %d rows (expected ~51,000+)",
            len(processed),
        )

    log_dataset_stats(processed)
    _atomic_write_parquet(processed, cache_path)
    return processed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest Zomato restaurant dataset")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Download, preprocess, and write Parquet cache",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download and overwrite existing cache",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args(argv)

    _configure_logging(args.verbose)

    if not args.ingest:
        parser.print_help()
        return 1

    settings = get_settings()

    try:
        df = ingest_dataset(settings, force=args.force)
        print(f"\nIngestion complete: {len(df)} restaurants cached at {settings.data_cache_path}")
        print(f"Unique cities: {df['city'].nunique()}")
        print(f"Sample cities: {', '.join(df['city'].value_counts().head(5).index.tolist())}")
        return 0
    except DataLoadError as exc:
        logger.error("%s", exc)
        return 1
    except DataValidationError as exc:
        logger.error("%s", exc)
        return 1
    except Exception as exc:
        logger.exception("Ingestion failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
