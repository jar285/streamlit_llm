"""Main entry point for the Streamlit chat application."""
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import app module from the same package
from llm_chat.app import run_app

def main() -> None:
    """Main entry point for the application."""
    try:
        run_app()
    except Exception as e:
        logger.exception(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()