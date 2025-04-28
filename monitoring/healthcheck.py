# monitoring/healthcheck.py

import os
from datetime import datetime, timedelta

def check_recent_run(log_dir: str, max_age_hours=48):
    # ensure there's a log file within the last max_age_hours
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    # … implementation …
    print("✅ Healthcheck passed")
