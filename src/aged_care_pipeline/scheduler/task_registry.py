# scheduler/task_registry.py

import yaml

from aged_care_pipeline.services.operations_service import OperationsService


def load_tasks():
    with open("config/schedules.yaml") as f:
        cfg = yaml.safe_load(f)
    tasks = []
    for name, spec in cfg.items():
        if name == "operations":
            svc = OperationsService()
            tasks.append({"id": name, "func": svc.run, "cron": spec["cron"]})
    return tasks
