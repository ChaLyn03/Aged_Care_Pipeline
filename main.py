# main.py
import os
import argparse
from utils.logger import setup_logger
from services.operations_service import OperationsService
from scrapers.operations_scraper import OperationsScraper
from parsers.operations_parser import OperationsParser
from writers.csv_writer import CSVWriter
import pandas as pd
from config.global_settings import NIDS_CSV

def main():
    # 1) parse CLI
    p = argparse.ArgumentParser(prog="aged-care-pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    # full pipeline
    run = sub.add_parser("run", help="scrape → parse → write")
    run.add_argument("--limit",    type=int,   help="only first N NIDs")
    run.add_argument("-v", "--verbose", action="store_true", help="DEBUG logs")

    # scraper only
    scr = sub.add_parser("scrape", help="just run scraper")
    scr.add_argument("--limit",    type=int)
    scr.add_argument("-v", "--verbose", action="store_true")

    # parser only (one JSON file)
    par = sub.add_parser("parse", help="just run parser on a single JSON")
    par.add_argument("json_file", help="path to raw JSON")
    par.add_argument("-v", "--verbose", action="store_true")

    # writer only (one records list saved as CSV)
    wri = sub.add_parser("write", help="just run writer on a small list")
    wri.add_argument("records_file", help="path to a .json with list[dict]")
    wri.add_argument("-v", "--verbose", action="store_true")

    args = p.parse_args()

    # 2) setup logging
    if args.verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"
    setup_logger()

    # 3) handle commands
    if args.cmd == "run":
        if args.limit is not None:
            os.environ["LIMIT"] = str(args.limit)
        svc = OperationsService()
        svc.run()

    elif args.cmd == "scrape":
        if args.limit is not None:
            os.environ["LIMIT"] = str(args.limit)
        from config.global_settings import LIMIT
        # read NIDs
        nids = pd.read_csv(NIDS_CSV).nid.dropna().astype(int).tolist()
        nids = nids[:LIMIT] if LIMIT else nids
        scraper = OperationsScraper()
        for i,nid in enumerate(nids,1):
            scraper.scrape(nid)

    elif args.cmd == "parse":
        import json
        with open(args.json_file) as f:
            raw = json.load(f)
        from parsers.operations_parser import OperationsParser
        rows = OperationsParser().parse(raw)
        logger = __import__("logging").getLogger("parse-only")
        logger.info(f"Parsed {len(rows)} rows")
        print(rows)  # or save to stdout

    elif args.cmd == "write":
        import json
        with open(args.records_file) as f:
            records = json.load(f)
        CSVWriter().write(records, f"test_output.csv")
        logger = __import__("logging").getLogger("write-only")
        logger.info("Wrote test_output.csv")

if __name__ == "__main__":
    main()
