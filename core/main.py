import argparse
import uvicorn
import server
from runtime import run_cli
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def main():
    parser = argparse.ArgumentParser(description="Calvin Core Runtime")
    parser.add_argument("--serve", action="store_true", help="Run FastAPI server")
    parser.add_argument("--cli", action="store_true", help="Run CLI mode")
    args = parser.parse_args()

    if args.serve:
        logging.info("Starting FastAPI server...")
        uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
    elif args.cli:
        logging.info("Launching CLI mode...")
        run_cli()
    else:
        logging.warning("No mode selected. Use --serve or --cli")
        print("No mode selected. Use --serve or --cli")

if __name__ == "__main__":
    main()
