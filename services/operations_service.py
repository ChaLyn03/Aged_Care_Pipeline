# services/operations_service.py

import pandas as pd
from datetime import datetime
from scrapers.operations_scraper import OperationsScraper
from parsers.operations.operations_parser import OperationsParser
from writers.csv_writer import CSVWriter
from config.global_settings import NIDS_CSV
from utils.limiter import apply_limit

class OperationsService:
    def __init__(self):
        self.scraper = OperationsScraper()
        self.parser  = OperationsParser()
        self.writer  = CSVWriter()

    def run(self) -> None:
        df = pd.read_csv(NIDS_CSV)
        nids = apply_limit(df.nid.dropna().astype(int).tolist())
        all_rows = []
        for i, nid in enumerate(nids, 1):
            raw = self.scraper.scrape(nid)
            parsed = self.parser.parse(raw)
            all_rows.extend(parsed)
            print(f"[{i}/{len(nids)}] NID {nid} → {len(parsed)} rows")
        date = datetime.now().strftime("%Y%m%d")
        out_file = f"operations_{date}.csv"
        self.writer.write(all_rows, out_file)
