import argparse
import json

from .baseline import baseline
from .benchmark import benchmark
from .db import connection, initialize
from .evaluation import evaluate
from .graph import start_graph
from .indexing import index_posts
from .ranking import generate
from .retrieval import generate_embedding
from .scheduling import schedule_active
from .seed import seed
from .source_demo import change_post, relay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=[
            "init",
            "seed",
            "status",
            "baseline",
            "source-post",
            "relay",
            "index",
            "embedding",
            "generate",
            "graph",
            "evaluate",
            "benchmark",
            "schedule",
        ],
    )
    parser.add_argument("--user", type=int, default=1)
    parser.add_argument("--strategy", choices=["latest", "popular"], default="latest")
    parser.add_argument("--post", type=int, default=1001)
    parser.add_argument("--body", default="Python PostgreSQL 백엔드 실습")
    parser.add_argument("--pause-after-rerank", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        initialize()
        result = {"schema": "ready"}
    elif args.command == "seed":
        result = seed()
    elif args.command == "baseline":
        result = baseline(args.user, args.strategy)
    elif args.command == "source-post":
        result = change_post(args.post, args.body)
    elif args.command == "relay":
        result = relay()
    elif args.command == "index":
        result = index_posts()
    elif args.command == "embedding":
        result = generate_embedding(args.user)
    elif args.command == "generate":
        result = generate(args.user)
    elif args.command == "graph":
        result = start_graph(args.user, args.pause_after_rerank)
    elif args.command == "evaluate":
        result = evaluate()
    elif args.command == "benchmark":
        result = benchmark(args.user)
    elif args.command == "schedule":
        result = schedule_active()
    else:
        with connection() as conn:
            result = {
                "posts": conn.execute("SELECT count(*) AS n FROM posts").fetchone()["n"],
                "users": conn.execute("SELECT count(*) AS n FROM users").fetchone()["n"],
            }
    print(json.dumps(result, ensure_ascii=False, default=str))
