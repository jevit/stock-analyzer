"""
Entry point for Hugging Face Spaces deployment.

This file is required by Hugging Face Spaces which expects an app.py
at the root of the repository.

For Streamlit Cloud, this file is not used - it directly runs app/main.py
"""
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run the main app
if __name__ == "__main__":
    from app.main import main
    main()
