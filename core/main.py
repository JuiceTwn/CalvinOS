import argparse
import uvicorn
from core import server
from runtime import run_cli

def main():
    parser = argparse.ArgumentParser(description="Calvin Core Runtime")
    parser.add_argument("--serve", action="store_true", help="Run FastAPI server")
    parser.add_argument("--cli", action="store_true", help="Run CLI mode")
    args = parser.parse_args()

    if args.serve:
        uvicorn.run("core.server:app", host="0.0.0.0", port=8000, reload=False)
    elif args.cli:
        run_cli()
    else:
        print("No mode selected. Use --serve or --cli")

if __name__ == "__main__":
    main()
