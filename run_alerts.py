#!/usr/bin/env python
"""
Script to run daily analysis and send Telegram alerts.

Usage:
    python run_alerts.py [--min-score 75] [--force-refresh]

Can be scheduled with Windows Task Scheduler or cron.
"""
import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from src.utils.helpers import load_tickers, setup_logging
from src.data.downloader import download_all_tickers
from src.indicators.technical import calculate_indicators
from src.scoring.scorer import SignalScorer
from src.alerts.telegram import TelegramNotifier
from loguru import logger


def main():
    """Run analysis and send alerts."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Stock Analyzer - Daily Alerts")
    parser.add_argument(
        "--min-score",
        type=int,
        default=75,
        help="Minimum score for alerts (default: 75)"
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force data refresh (ignore cache)"
    )
    parser.add_argument(
        "--tickers-file",
        type=str,
        default=None,
        help="Path to tickers file"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test Telegram connection only"
    )
    args = parser.parse_args()

    # Setup
    setup_logging()
    settings = get_settings()

    # Test mode
    notifier = TelegramNotifier()

    if args.test:
        logger.info("Testing Telegram connection...")
        if not notifier.is_configured():
            logger.error("Telegram not configured. Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")
            sys.exit(1)

        if notifier.test_connection():
            logger.info("✅ Telegram test successful!")
        else:
            logger.error("❌ Telegram test failed!")
            sys.exit(1)
        return

    # Load tickers
    tickers_file = Path(args.tickers_file) if args.tickers_file else settings.tickers_file

    try:
        tickers = load_tickers(tickers_file)
    except FileNotFoundError:
        logger.error(f"Tickers file not found: {tickers_file}")
        sys.exit(1)

    if not tickers:
        logger.error("No tickers to analyze")
        sys.exit(1)

    logger.info(f"Analyzing {len(tickers)} tickers...")

    # Download data
    data, failed = download_all_tickers(
        tickers,
        use_cache=True,
        force_refresh=args.force_refresh
    )

    if failed:
        logger.warning(f"Failed to download: {failed}")

    # Calculate indicators
    for ticker, df in data.items():
        data[ticker] = calculate_indicators(df)

    # Run analysis
    scorer = SignalScorer()
    analyses = scorer.analyze_watchlist(data, min_score=args.min_score)

    # Log summary
    signals = [a for a in analyses if a.has_signal]
    logger.info(f"Analysis complete: {len(signals)} signals with score >= {args.min_score}")

    for a in signals[:10]:
        logger.info(f"  {a.ticker}: {a.global_score}/100 - {a.best_strategy}")

    # Send Telegram alert
    if not notifier.is_configured():
        logger.warning("Telegram not configured - skipping notification")
        logger.info("Set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID environment variables")
    else:
        if notifier.send_daily_alert(analyses, min_score=args.min_score):
            logger.info("✅ Telegram alert sent successfully")
        else:
            logger.error("❌ Failed to send Telegram alert")

    logger.info("Done!")


if __name__ == "__main__":
    main()
