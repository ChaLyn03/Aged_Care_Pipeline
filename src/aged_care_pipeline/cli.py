# main.py
import argparse
import glob
import importlib
import json
import logging
import os
from datetime import datetime

import pandas as pd

from aged_care_pipeline.config import global_settings as gs
from aged_care_pipeline.utils.limiter import apply_limit
from aged_care_pipeline.utils.logger import setup_logger
from aged_care_pipeline.writers.csv_writer import CSVWriter

# Pipeline registry: add your pipelines here
PIPELINES = {
    "operations": {
        "nids_csv": gs.NIDS_CSV,
        "scraper": (
            "aged_care_pipeline.scrapers.operations_scraper",
            "OperationsScraper",
        ),
        "parser": (
            "aged_care_pipeline.parsers.operations.operations_parser",
            "OperationsParser",
        ),
        "prefix": "operations",
    },
    "rads": {
        "nids_csv": gs.RADS_NIDS_CSV,
        "scraper": ("aged_care_pipeline.scrapers.rads_scraper", "RadsScraper"),
        "parser": ("aged_care_pipeline.parsers.rads.rads_parser", "RadsParser"),
        "prefix": "rads",
    },
}


def add_subcommands(subparsers):
    # Shared verbose
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("-v", "--verbose", action="store_true", help="DEBUG logs")

    # run
    run_p = subparsers.add_parser(
        "run", parents=[parent], help="scrape → parse → write"
    )
    run_p.add_argument("--limit", type=int, help="only first N items")

    # scrape
    scr_p = subparsers.add_parser("scrape", parents=[parent], help="only run scraper")
    scr_p.add_argument("--limit", type=int)

    # parse
    par_p = subparsers.add_parser(
        "parse", parents=[parent], help="only run parser on JSON"
    )
    par_p.add_argument("json_file", help="path to raw JSON file")

    # write
    wri_p = subparsers.add_parser(
        "write", parents=[parent], help="only run writer on records JSON"
    )
    wri_p.add_argument("records_file", help="path to JSON list of dicts")

    # cleanup
    clean_p = subparsers.add_parser(
        "cleanup", parents=[parent], help="merge & cleanup raw/interim"
    )
    clean_p.add_argument(
        "--keep-raw", action="store_true", help="retain per-ID raw files after merging"
    )

    return parent


def _do_cleanup(pipeline: str, raw_dir: str, interim_dir: str, keep_raw: bool):
    """
    Merge all per-ID raw JSONs for `pipeline`, archive them, delete
    originals and purge interim.  `keep_raw` controls retention of
    the individual raw files.
    """
    cleanup_logger = logging.getLogger(f"{pipeline}.cleanup")
    archive_root = os.path.join(gs.RAW_DIR, "archive", pipeline)
    os.makedirs(archive_root, exist_ok=True)

    # Gather raw jsons, skipping already-merged
    raw_paths = [
        p
        for p in glob.glob(f"{raw_dir}/*.json")
        if not os.path.basename(p).startswith(f"{pipeline}_all_raw_")
    ]

    # Load and append
    merged = []
    for p in raw_paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                merged.append(json.load(f))
        except Exception as e:
            cleanup_logger.warning(f"Skipping {p}: {e}")

    # Write single big archive file
    ts = datetime.now().strftime("%d_%m_%Y")
    archive_file = os.path.join(archive_root, f"{pipeline}_all_raw_{ts}.json")
    with open(archive_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    cleanup_logger.info(f"Merged {len(merged)} raw files → {archive_file}")

    # Delete per-ID raw files (unless we want to keep them)
    if not keep_raw:
        for p in raw_paths:
            try:
                os.remove(p)
            except Exception as e:
                cleanup_logger.warning(f"Failed to delete {p}: {e}")
        cleanup_logger.info(f"Deleted {len(raw_paths)} raw JSONs")

    # Purge interim JSONs
    interim_paths = glob.glob(f"{interim_dir}/*.json")
    for p in interim_paths:
        try:
            os.remove(p)
        except Exception as e:
            cleanup_logger.warning(f"Failed to delete interim file {p}: {e}")
    cleanup_logger.info(f"Deleted {len(interim_paths)} interim JSONs")


def main():
    parser = argparse.ArgumentParser(prog="aged-care-pipeline")
    pipe_sp = parser.add_subparsers(
        dest="pipeline", required=True, help="choose a pipeline to run"
    )

    # for each pipeline, add its subcommands
    for name in PIPELINES:
        p = pipe_sp.add_parser(name, help=f"commands for {name} pipeline")
        sub = p.add_subparsers(dest="cmd", required=True)
        add_subcommands(sub)

    args = parser.parse_args()

    # configure logging
    if getattr(args, "verbose", False):
        os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ.setdefault("LOG_LEVEL", "INFO")
    setup_logger()
    logger = logging.getLogger(f"{args.pipeline}")

    # pipeline config
    if args.pipeline not in PIPELINES:
        logger.error(f"Unknown pipeline: {args.pipeline}")
        return
    conf = PIPELINES[args.pipeline]

    # prepare dirs
    raw_dir = os.path.join(gs.RAW_DIR, args.pipeline)
    interim_dir = os.path.join(gs.INTERIM_DIR, args.pipeline)
    output_dir = os.path.join(gs.OUTPUT_DIR, args.pipeline)
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(interim_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    # dynamic import
    mod_scr, cls_scr = conf["scraper"]
    mod_par, cls_par = conf["parser"]
    Scraper = getattr(importlib.import_module(mod_scr), cls_scr)
    Parser = getattr(importlib.import_module(mod_par), cls_par)

    # run commands
    if args.cmd == "run":
        if args.limit is not None:
            os.environ["LIMIT"] = str(args.limit)

        df = pd.read_csv(conf["nids_csv"])
        nids = df.nid.dropna().astype(int).tolist()
        nids = apply_limit(nids)

        scraper = Scraper(raw_dir=raw_dir)
        parser_ = Parser()
        all_rows = []

        # — Validation state —
        expected_nids = set(nids)
        scraped_nids = set()

        # We'll discover expected_fields dynamically on first non-empty row.
        expected_fields = None

        for idx, nid in enumerate(nids, start=1):
            logger.info(f"[{idx}/{len(nids)}] Scraping {nid}")
            raw = scraper.scrape(nid)

            logger.info(f"[{idx}/{len(nids)}] Parsing {nid}")
            rows = parser_.parse(raw)

            # save interim
            ts = datetime.now().strftime("%d_%m_%Y")
            fname = f"{conf['prefix']}_{nid}_{ts}_parsed.json"
            ipath = os.path.join(interim_dir, fname)
            with open(ipath, "w", encoding="utf-8") as wf:
                json.dump(rows, wf, ensure_ascii=False, indent=2)
            logger.info(f"Parsed → {ipath}")
            parsed = parser_.parse(raw)

            # track NID coverage
            if parsed:
                scraped_nids.add(nid)

                # On the very first parsed row, grab its field‐count
                if expected_fields is None:
                    expected_fields = len(parsed[0].keys())
                    logger.debug(f"Detected {expected_fields} total fields per row")

                # For each row (usually one per NID) compute completeness
                for row in parsed:
                    present = sum(
                        1 for v in row.values() if v not in (None, "", [], {})
                    )
                    missing = expected_fields - present
                    pct_miss = missing / expected_fields * 100

                    tag = "COMPLETE" if missing == 0 else "INCOMPLETE"
                    level = logging.DEBUG if missing == 0 else logging.WARNING
                    logger.log(
                        level,
                        f"[{tag}] NID {nid}: "
                        f"{present}/{expected_fields} fields present, "
                        f"{missing} missing ({pct_miss:.1f}%)",
                    )

                all_rows.extend(parsed)
            else:
                logger.warning(f"NID {nid} returned no data; skipping")

        # write CSV
        ts = datetime.now().strftime("%d_%m_%Y")
        ofile = f"{conf['prefix']}_{ts}.csv"
        CSVWriter(output_dir=output_dir).write(all_rows, ofile)
        total_expected = len(expected_nids)
        total_seen = len(scraped_nids)
        missed_nids = expected_nids - scraped_nids
        pct_covered = total_seen / total_expected * 100

        logger.info(
            f"NID coverage: {total_seen}/{total_expected} "
            f"({pct_covered:.1f}%) scraped; "
            f"{len(missed_nids)} missing: {sorted(missed_nids)}"
        )

        # finally, write your CSV
        CSVWriter(output_dir=output_dir).write(all_rows, ofile)
        logger.info(f"Wrote CSV → {os.path.join(output_dir, ofile)}")

        # now automatically clean up raw+interim
        _do_cleanup(
            pipeline=args.pipeline,
            raw_dir=raw_dir,
            interim_dir=interim_dir,
            keep_raw=False,
        )

    elif args.cmd == "scrape":
        if args.limit is not None:
            os.environ["LIMIT"] = str(args.limit)
        df = pd.read_csv(conf["nids_csv"])
        nids = apply_limit(df.nid.dropna().astype(int).tolist())
        Scraper(raw_dir=raw_dir).bulk(nids)

    elif args.cmd == "parse":
        with open(args.json_file, encoding="utf-8") as f:
            raw = json.load(f)
        rows = Parser().parse(raw)
        logger.info(f"Parsed {len(rows)} rows from {args.json_file}")
        base = os.path.splitext(os.path.basename(args.json_file))[0]
        out = f"{base}_parsed.json"
        with open(os.path.join(interim_dir, out), "w", encoding="utf-8") as wf:
            json.dump(rows, wf, ensure_ascii=False, indent=2)
        logger.info(f"Saved → {os.path.join(interim_dir, out)}")

    elif args.cmd == "write":
        with open(args.records_file, encoding="utf-8") as f:
            records = json.load(f)
        fname = os.path.basename(args.records_file).replace(".json", ".csv")
        CSVWriter(output_dir=output_dir).write(records, fname)
        logger.info(f"Wrote CSV → {os.path.join(output_dir, fname)}")

    elif args.cmd == "cleanup":
        # allow DEBUG if requested
        if getattr(args, "verbose", False):
            os.environ["LOG_LEVEL"] = "DEBUG"
            setup_logger()
        cleanup_logger = logging.getLogger(f"{args.pipeline}.cleanup")

        # A) Prepare pipeline‐specific archive dir
        archive_root = os.path.join(gs.RAW_DIR, "archive", args.pipeline)
        os.makedirs(archive_root, exist_ok=True)

        # B) Find all per‐NID raw JSONs for this pipeline
        raw_paths = [
            p
            for p in glob.glob(f"{raw_dir}/*.json")
            if not os.path.basename(p).startswith("all_raw_")
        ]

        # C) Load & append each JSON object
        merged = []
        for p in raw_paths:
            try:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)
                merged.append(data)  # <<< append the dict, not extend!
            except Exception as e:
                cleanup_logger.warning(f"Skipping {p}: {e}")

        # D) Write out one big archive file
        timestamp = datetime.now().strftime("%d_%m_%Y")
        # put merged files in data/raw/archive/<pipeline>/
        archive_root = os.path.join(gs.RAW_DIR, "archive", args.pipeline)
        os.makedirs(archive_root, exist_ok=True)
        archive_file = os.path.join(
            archive_root, f"{args.pipeline}_all_raw_{timestamp}.json"
        )
        with open(archive_file, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        cleanup_logger.info(f"Merged {len(merged)} files into {archive_file}")

        # E) Delete originals (unless user asked to keep them)
        if not args.keep_raw:
            for p in raw_paths:
                try:
                    os.remove(p)
                except Exception as e:
                    cleanup_logger.warning(f"Failed to delete {p}: {e}")
            cleanup_logger.info(f"Deleted {len(raw_paths)} individual raw JSONs")

        # F) Purge all interim JSONs
        interim_paths = glob.glob(f"{interim_dir}/*.json")
        for p in interim_paths:
            try:
                os.remove(p)
            except Exception as e:
                cleanup_logger.warning(f"Failed to delete interim file {p}: {e}")
        cleanup_logger.info(f"Deleted {len(interim_paths)} interim JSONs")


if __name__ == "__main__":
    main()
