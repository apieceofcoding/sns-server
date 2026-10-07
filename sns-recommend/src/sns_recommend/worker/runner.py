from __future__ import annotations

import argparse
import json
import logging
import time

import psycopg
from redis.exceptions import RedisError

from sns_recommend.data.indexing import index_posts
from sns_recommend.pipelines.graph import run_graph
from sns_recommend.recommenders.retrieval import process_profile
from sns_recommend.storage.jobs import claim, finish, retry
from sns_recommend.worker.scheduler import schedule_active

logger = logging.getLogger(__name__)


def run_one() -> bool:
    job = claim()
    if not job:
        return False
    try:
        if job["kind"] == "index":
            if job["post_id"] is None:
                raise ValueError("index job requires post_id")
            index_posts([job["post_id"]])
        elif job["kind"] == "build":
            run_graph(job)
            return True
        else:
            if job["user_id"] is None:
                raise ValueError("profile job requires user_id")
            process_profile(job["user_id"])
        finish(job)
    except Exception as exc:
        logger.warning("Job %s (%s) failed: %s", job["id"], job["kind"], type(exc).__name__)
        retry(job, type(exc).__name__)
    return True


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.once:
        print(json.dumps({"processed": run_one()}))
    else:
        last_schedule = 0.0
        while True:
            try:
                if time.monotonic() - last_schedule >= 30:
                    schedule_active()
                    last_schedule = time.monotonic()
                processed = run_one()
            except (psycopg.Error, RedisError) as exc:
                logger.warning("Worker storage unavailable: %s", type(exc).__name__)
                processed = False
            if not processed:
                time.sleep(1)
