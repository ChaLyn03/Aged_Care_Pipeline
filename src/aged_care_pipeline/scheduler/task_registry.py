# src/aged_care_pipeline/scheduler/task_registry.py

from importlib.resources import as_file, files

import yaml

from aged_care_pipeline.services.operations_service import OperationsService


def load_tasks():
    # Locate the bundled schedules.yaml in our package
    resource = files("aged_care_pipeline.config").joinpath("schedules.yaml")
    # Copy it out to a real filesystem path so yaml can read it
    with as_file(resource) as path:
        cfg = yaml.safe_load(path.read_text())

    tasks = []
    for name, spec in cfg.items():
        if name == "operations":
            svc = OperationsService()
            tasks.append(
                {
                    "id": name,
                    "func": svc.run,
                    "cron": spec["cron"],
                }
            )
    return tasks
