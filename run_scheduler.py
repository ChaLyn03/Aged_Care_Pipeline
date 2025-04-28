# run_scheduler.py

from scheduler.apscheduler_runner import APSchedulerRunner

def main():
    runner = APSchedulerRunner()
    runner.start()

if __name__ == "__main__":
    main()
