# run_pipeline.py — orchestrates the full ingestion + transform pipeline
import subprocess
import logging
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON = PROJECT_ROOT / "venv" / "Scripts" / "python.exe"
DBT = PROJECT_ROOT / "venv" / "Scripts" / "dbt.exe"
DBT_PROJECT_DIR = PROJECT_ROOT / "training_load"

LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"pipeline_{datetime.now():%Y%m%d_%H%M%S}.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def run_step(name, args, cwd):
    logging.info(f"Starting: {name}")
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        logging.info(result.stdout)
    if result.returncode != 0:
        logging.error(f"{name} FAILED (exit code {result.returncode})")
        if result.stderr:
            logging.error(result.stderr)
        return False
    logging.info(f"{name} completed successfully")
    return True


def publish_dashboard_data():
    if not run_step(
        "export_dashboard_data",
        [str(PYTHON), "pipeline/export_dashboard_data.py"],
        cwd=PROJECT_ROOT,
    ):
        return False

    logging.info("Starting: git add docs/data")
    add_result = subprocess.run(
        ["git", "add", "docs/data"], cwd=PROJECT_ROOT, capture_output=True, text=True
    )
    if add_result.returncode != 0:
        logging.error(f"git add FAILED: {add_result.stderr}")
        return False

    # Check directly whether anything under docs/data was actually staged,
    # independent of whatever else may be sitting unstaged/untracked
    # elsewhere in the working tree (e.g. edits you're mid-way through).
    diff_result = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--", "docs/data"],
        cwd=PROJECT_ROOT,
    )
    if diff_result.returncode == 0:
        logging.info("No dashboard data changes to commit — skipping commit and push.")
        return True

    logging.info("Starting: git commit")
    commit_result = subprocess.run(
        ["git", "commit", "-m", f"Update dashboard data ({datetime.now():%Y-%m-%d %H:%M})",
         "--", "docs/data"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if commit_result.returncode != 0:
        logging.error(f"git commit FAILED: {commit_result.stdout} {commit_result.stderr}")
        return False

    logging.info("Starting: git push")
    push_result = subprocess.run(
        ["git", "push"], cwd=PROJECT_ROOT, capture_output=True, text=True
    )
    if push_result.returncode != 0:
        logging.error(f"git push FAILED: {push_result.stderr}")
        return False

    logging.info("Dashboard data committed and pushed successfully.")
    return True


def main():
    steps_ok = True

    print("Refreshing activity data (intervals.icu)...")
    steps_ok &= run_step(
        "ingest_intervals",
        [str(PYTHON), "pipeline/ingest_intervals.py"],
        cwd=PROJECT_ROOT,
    )

    print("Refreshing weather data...")
    steps_ok &= run_step(
        "ingest_weather",
        [str(PYTHON), "pipeline/ingest_weather.py"],
        cwd=PROJECT_ROOT,
    )

    print("Rebuilding dbt models...")
    steps_ok &= run_step(
        "dbt_run",
        [str(DBT), "run"],
        cwd=DBT_PROJECT_DIR,
    )

    print("Publishing dashboard data...")
    steps_ok &= publish_dashboard_data()

    if steps_ok:
        print(f"Done — pipeline completed successfully. Log: {log_file}")
        logging.info("Pipeline completed successfully end-to-end.")
    else:
        print(f"FAILED — check the log for details: {log_file}")
        logging.error("Pipeline completed with at least one failed step — check the log above.")


if __name__ == "__main__":
    main()