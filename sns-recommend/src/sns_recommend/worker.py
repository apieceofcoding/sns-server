import argparse
import json
import time

from .graph import run_graph
from .indexing import index_posts
from .jobs import claim, finish, retry
from .retrieval import process_profile
from .scheduling import schedule_active


def run_one():
    job = claim()
    if not job:
        return False
    try:
        if job["kind"] == "index":
            index_posts([job["post_id"]])
        elif job["kind"] == "build":
            run_graph(job)
            return True
        else:
            process_profile(job["user_id"])
        finish(job)
    except Exception as exc:
        retry(job, type(exc).__name__)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.once:
        print(json.dumps({"processed": run_one()}))
    else:
        last_schedule = 0
        while True:
            if time.monotonic() - last_schedule >= 30:
                schedule_active()
                last_schedule = time.monotonic()
            if not run_one():
                time.sleep(1)


if __name__ == "__main__":
    main()
