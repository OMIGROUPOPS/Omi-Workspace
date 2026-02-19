"""
OMI Edge Backend - Main Entry Point

Starts the FastAPI server and background scheduler.

Usage:
    python main.py          # Start server + scheduler
    python main.py --once   # Run one analysis cycle and exit
"""
import os
import sys
import logging
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""

    if "--once" in sys.argv:
        from scheduler import run_once
        logger.info("Running single analysis cycle...")
        run_once()
        return

    port = int(os.environ.get("PORT", 8000))
    print(f"SERVER STARTING ON PORT {port}", flush=True)
    logger.info(f"Starting uvicorn on 0.0.0.0:{port} — scheduler will start AFTER server is ready")
    try:
        from api.server import app
        uvicorn.run(app, host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
