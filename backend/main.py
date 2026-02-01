"""
OMI Edge Backend - Main Entry Point

Starts the FastAPI server and background scheduler.

Usage:
    python main.py          # Start server + scheduler
    python main.py --once   # Run one analysis cycle and exit
"""
import sys
import logging
import uvicorn

from scheduler import start_scheduler, run_once

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    
    if "--once" in sys.argv:
        logger.info("Running single analysis cycle...")
        run_once()
        return
    
    logger.info("Starting OMI Edge backend...")
    scheduler = start_scheduler()

    # Skip initial analysis - let the scheduler handle it
    # This ensures the API server starts immediately
    logger.info("Skipping initial analysis (will run on schedule)...")
    # try:
    #     run_once()
    # except Exception as e:
    #     logger.error(f"Initial analysis failed: {e}")

    logger.info("Starting API server on port 8000...")
    try:
        from api.server import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        scheduler.shutdown()


if __name__ == "__main__":
    main()