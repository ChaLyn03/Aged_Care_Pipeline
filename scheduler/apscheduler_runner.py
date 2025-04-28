# scheduler/apscheduler_runner.py

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from interfaces.base_scheduler import BaseScheduler
from .task_registry import load_tasks

class APSchedulerRunner(BaseScheduler):
    def start(self) -> None:
        sched = BlockingScheduler()
        for t in load_tasks():
            trigger = CronTrigger.from_crontab(t["cron"])
            sched.add_job(t["func"], trigger, id=t["id"])
            print(f"Scheduled {t['id']} → {t['cron']}")
        sched.start()
