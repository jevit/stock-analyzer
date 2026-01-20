"""
Cache manager for price data using Parquet files.
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import pandas as pd
from loguru import logger

from config.settings import get_settings


class CacheManager:
    """Manages local cache of price data using Parquet format."""

    def __init__(self):
        """Initialize cache manager."""
        self.settings = get_settings()
        self.cache_dir = self.settings.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, ticker: str) -> Path:
        """Get cache file path for a ticker."""
        return self.cache_dir / f"{ticker.upper()}.parquet"

    def _get_metadata_path(self, ticker: str) -> Path:
        """Get metadata file path for a ticker."""
        return self.cache_dir / f"{ticker.upper()}_meta.txt"

    def is_cache_valid(self, ticker: str) -> bool:
        """
        Check if cache exists and is still valid (not expired).

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if cache is valid, False otherwise
        """
        cache_path = self._get_cache_path(ticker)
        meta_path = self._get_metadata_path(ticker)

        if not cache_path.exists() or not meta_path.exists():
            return False

        try:
            with open(meta_path, "r") as f:
                cached_time = datetime.fromisoformat(f.read().strip())

            expiry_time = cached_time + timedelta(hours=self.settings.cache_expiry_hours)
            is_valid = datetime.now() < expiry_time

            if is_valid:
                logger.debug(f"Cache valid for {ticker} (cached at {cached_time})")
            else:
                logger.debug(f"Cache expired for {ticker}")

            return is_valid

        except (ValueError, IOError) as e:
            logger.warning(f"Error reading cache metadata for {ticker}: {e}")
            return False

    def get_cached_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """
        Retrieve cached data for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with price data or None if not cached/invalid
        """
        if not self.is_cache_valid(ticker):
            return None

        cache_path = self._get_cache_path(ticker)

        try:
            df = pd.read_parquet(cache_path)
            logger.info(f"Loaded {ticker} from cache ({len(df)} rows)")
            return df
        except Exception as e:
            logger.error(f"Error reading cache for {ticker}: {e}")
            return None

    def save_to_cache(self, ticker: str, data: pd.DataFrame) -> bool:
        """
        Save data to cache.

        Args:
            ticker: Stock ticker symbol
            data: DataFrame with price data

        Returns:
            True if saved successfully, False otherwise
        """
        cache_path = self._get_cache_path(ticker)
        meta_path = self._get_metadata_path(ticker)

        try:
            # Save data as parquet
            data.to_parquet(cache_path, index=True)

            # Save metadata (timestamp)
            with open(meta_path, "w") as f:
                f.write(datetime.now().isoformat())

            logger.debug(f"Cached {ticker} ({len(data)} rows)")
            return True

        except Exception as e:
            logger.error(f"Error caching {ticker}: {e}")
            return False

    def clear_cache(self, ticker: Optional[str] = None) -> int:
        """
        Clear cache for a specific ticker or all tickers.

        Args:
            ticker: Ticker to clear (None = clear all)

        Returns:
            Number of files deleted
        """
        deleted = 0

        if ticker:
            # Clear specific ticker
            for path in [self._get_cache_path(ticker), self._get_metadata_path(ticker)]:
                if path.exists():
                    path.unlink()
                    deleted += 1
        else:
            # Clear all cache
            for path in self.cache_dir.glob("*"):
                if path.is_file():
                    path.unlink()
                    deleted += 1

        logger.info(f"Cleared {deleted} cache files")
        return deleted

    def get_cache_info(self) -> dict:
        """Get cache statistics."""
        parquet_files = list(self.cache_dir.glob("*.parquet"))
        total_size = sum(f.stat().st_size for f in parquet_files)

        return {
            "num_tickers": len(parquet_files),
            "total_size_mb": total_size / (1024 * 1024),
            "cache_dir": str(self.cache_dir),
        }
