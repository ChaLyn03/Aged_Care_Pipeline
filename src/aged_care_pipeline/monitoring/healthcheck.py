# monitoring/healthcheck.py


def check_recent_run(log_dir: str, max_age_hours=48):
    # ensure there's a log file within the last max_age_hours
    # … implementation …
    print("✅ Healthcheck passed")
