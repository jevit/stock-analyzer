#!/usr/bin/env python3
"""
Automatic Stock Scanner - Run periodically for alerts.

Usage:
    python scripts/auto_scanner.py [--min-score 75] [--dry-run] [--verbose]

Setup as Windows Task Scheduler:
    1. Open Task Scheduler
    2. Create Basic Task
    3. Set trigger (e.g., Daily at 18:00 after market close)
    4. Action: Start a program
       Program: python
       Arguments: C:\\path\\to\\stock-analyzer\\scripts\\auto_scanner.py
       Start in: C:\\path\\to\\stock-analyzer

Setup as cron (Linux/Mac):
    # Run at 6 PM every weekday
    0 18 * * 1-5 cd /path/to/stock-analyzer && python scripts/auto_scanner.py
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from loguru import logger
from config.settings import get_settings
from src.utils.helpers import load_tickers, setup_logging
from src.data.downloader import download_all_tickers
from src.indicators.technical import calculate_indicators
from src.scoring.scorer import SignalScorer
from src.alerts.telegram import TelegramNotifier
from src.alerts.email_notifier import EmailNotifier
from src.alerts.history import AlertHistory


def run_scan(
    min_score: int = 75,
    dry_run: bool = False,
    cooldown_hours: int = 24,
    force_refresh: bool = False
) -> dict:
    """
    Run a full scan and send alerts for strong signals.

    Args:
        min_score: Minimum score to trigger alert
        dry_run: If True, don't actually send alerts
        cooldown_hours: Hours before same alert can be sent again
        force_refresh: Force data refresh (ignore cache)

    Returns:
        Dictionary with scan results
    """
    settings = get_settings()
    results = {
        "timestamp": datetime.now().isoformat(),
        "tickers_scanned": 0,
        "signals_found": 0,
        "alerts_sent": 0,
        "alerts_skipped_duplicate": 0,
        "errors": []
    }

    # Load tickers
    try:
        tickers = load_tickers(settings.tickers_file)
        logger.info(f"Loaded {len(tickers)} tickers from {settings.tickers_file}")
    except FileNotFoundError:
        error = f"Tickers file not found: {settings.tickers_file}"
        logger.error(error)
        results["errors"].append(error)
        return results

    if not tickers:
        error = "No tickers to scan"
        logger.error(error)
        results["errors"].append(error)
        return results

    # Download data
    logger.info("Downloading market data...")
    data, failed = download_all_tickers(
        tickers,
        use_cache=True,
        force_refresh=force_refresh
    )

    if failed:
        logger.warning(f"Failed to download: {failed}")
        results["errors"].extend([f"Download failed: {t}" for t in failed])

    results["tickers_scanned"] = len(data)

    if not data:
        error = "No data downloaded"
        logger.error(error)
        results["errors"].append(error)
        return results

    # Calculate indicators
    logger.info("Calculating technical indicators...")
    for ticker, df in data.items():
        data[ticker] = calculate_indicators(df)

    # Run analysis
    logger.info("Analyzing signals...")
    scorer = SignalScorer()
    analyses = scorer.analyze_watchlist(data)

    # Filter by min score and has_signal
    strong_signals = [
        a for a in analyses
        if a.global_score >= min_score and a.has_signal
    ]
    results["signals_found"] = len(strong_signals)

    logger.info(f"Found {len(strong_signals)} signals with score >= {min_score}")

    if not strong_signals:
        logger.info("No strong signals found - no alerts to send")
        return results

    # Filter out duplicates
    history = AlertHistory(cooldown_hours=cooldown_hours)
    new_alerts = history.get_new_alerts(strong_signals)
    results["alerts_skipped_duplicate"] = len(strong_signals) - len(new_alerts)

    if not new_alerts:
        logger.info("All signals are duplicates - no new alerts to send")
        return results

    logger.info(f"New alerts to send: {len(new_alerts)}")

    # Log details
    for a in new_alerts:
        logger.info(f"  {a.ticker}: {a.best_strategy} (Score: {a.global_score})")

    # Send alerts (Email priority, then Telegram fallback)
    if dry_run:
        logger.info("[DRY RUN] Would send alerts for:")
        for a in new_alerts:
            logger.info(f"  - {a.ticker}: {a.best_strategy} (Score: {a.global_score})")
        results["alerts_sent"] = 0
    else:
        alert_sent = False

        # Try Email first
        email_notifier = EmailNotifier()
        if email_notifier.is_configured():
            logger.info("Sending email alert...")
            if email_notifier.send_daily_alert(new_alerts, min_score=0):
                results["alerts_sent"] = len(new_alerts)
                alert_sent = True
                logger.info(f"Successfully sent email with {len(new_alerts)} alerts")

                # Record sent alerts in history
                for a in new_alerts:
                    history.record_alert(
                        ticker=a.ticker,
                        strategy=a.best_strategy,
                        score=a.global_score,
                        price=a.close
                    )
            else:
                results["errors"].append("Failed to send email")
        else:
            logger.info("Email not configured, trying Telegram...")

        # Fallback to Telegram if email not sent
        if not alert_sent:
            telegram_notifier = TelegramNotifier()
            if telegram_notifier.is_configured():
                logger.info("Sending Telegram alert...")
                message = telegram_notifier.format_alert_message(new_alerts, min_score=0)

                if telegram_notifier.send_message(message):
                    results["alerts_sent"] = len(new_alerts)
                    alert_sent = True

                    # Record sent alerts in history
                    for a in new_alerts:
                        history.record_alert(
                            ticker=a.ticker,
                            strategy=a.best_strategy,
                            score=a.global_score,
                            price=a.close
                        )

                    logger.info(f"Successfully sent Telegram alert with {len(new_alerts)} signals")
                else:
                    results["errors"].append("Failed to send Telegram message")
            else:
                logger.warning("Neither Email nor Telegram configured - alerts not sent")
                logger.info("Configure Email or Telegram in .env file")
                results["errors"].append("No notification method configured")

    # Cleanup old history
    history.cleanup_old_records(days=30)

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automatic stock scanner with Telegram alerts"
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=75,
        help="Minimum score to trigger alert (default: 75)"
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=24,
        help="Hours before same ticker/strategy can alert again (default: 24)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run analysis but don't send alerts"
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force data refresh (ignore cache)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    if args.verbose:
        logger.add(sys.stderr, level="DEBUG")

    logger.info("=" * 50)
    logger.info("Stock Scanner - Starting automatic scan")
    logger.info(f"Min score: {args.min_score}, Cooldown: {args.cooldown}h")
    logger.info("=" * 50)

    try:
        results = run_scan(
            min_score=args.min_score,
            dry_run=args.dry_run,
            cooldown_hours=args.cooldown,
            force_refresh=args.force_refresh
        )

        # Print summary
        logger.info("")
        logger.info("=" * 50)
        logger.info("SCAN COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Tickers scanned:     {results['tickers_scanned']}")
        logger.info(f"Strong signals:      {results['signals_found']}")
        logger.info(f"Alerts sent:         {results['alerts_sent']}")
        logger.info(f"Duplicates skipped:  {results['alerts_skipped_duplicate']}")

        if results["errors"]:
            logger.warning(f"Errors: {len(results['errors'])}")
            for err in results["errors"]:
                logger.warning(f"  - {err}")

        # Exit code based on errors
        sys.exit(1 if results["errors"] and not results["alerts_sent"] else 0)

    except Exception as e:
        logger.exception(f"Scanner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
