# monitoring/alerting.py


def alert_on_failure(task_id: str, message: str):
    # e.g. send Slack or SMS
    print(f"🚨 ALERT [{task_id}]: {message}")
