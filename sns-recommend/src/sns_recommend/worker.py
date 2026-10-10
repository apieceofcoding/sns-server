import argparse
import json
import time
from .jobs import claim, finish
from .indexing import index_posts
from .retrieval import process_profile
from .ranking import generate


def run_one():
    job = claim()
    if not job:
        return False
    try:
        if job["kind"] == "index":
            index_posts([job["post_id"]])
        elif job["kind"] == "build":
            generate(job["user_id"],job["generation"],str(job["id"]),job["created_at"].timestamp())
        else:
            process_profile(job["user_id"])
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
