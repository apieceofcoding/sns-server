import argparse
import json
import time
from .jobs import claim, finish
from .indexing import index_posts


def run_one():
    job = claim(("index",))
    if not job:
        return False
    try:
        index_posts([job["post_id"]])
        finish(job)
    except Exception as exc:
        finish(job, "failed", type(exc).__name__)
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.once:
        print(json.dumps({"processed":run_one()}))
    else:
        while True:
            if not run_one():
                time.sleep(1)


if __name__ == "__main__":
    main()
