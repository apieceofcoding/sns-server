import argparse
import json
from .db import initialize, connection
from .seed import seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["init", "seed", "status"])
    args = parser.parse_args()
    if args.command == "init":
        initialize()
        result = {"schema": "ready"}
    elif args.command == "seed":
        result = seed()
    else:
        with connection() as conn:
            result = {"posts": conn.execute("SELECT count(*) AS n FROM posts").fetchone()["n"],
                      "users": conn.execute("SELECT count(*) AS n FROM users").fetchone()["n"]}
    print(json.dumps(result, ensure_ascii=False, default=str))
