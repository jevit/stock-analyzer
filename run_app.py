#!/usr/bin/env python
"""
Script to launch the Stock Analyzer Streamlit application.

Usage:
    python run_app.py

Or directly with streamlit:
    streamlit run app/main.py
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit application."""
    # Get the app path
    app_path = Path(__file__).parent / "app" / "main.py"

    if not app_path.exists():
        print(f"Error: Application not found at {app_path}")
        sys.exit(1)

    print("🚀 Starting Stock Analyzer...")
    print(f"   App path: {app_path}")
    print("")

    # Launch streamlit
    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", str(app_path)],
            check=True
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error launching application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
