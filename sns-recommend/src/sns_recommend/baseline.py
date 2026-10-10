import time
from .feed import publish
from .source import ordered_post_ids


def baseline(user_id, strategy="latest"):
    if strategy not in {"latest", "popular"}:
        raise ValueError("unsupported baseline")
    ids = ordered_post_ids(strategy)
    publish(user_id, ids, strategy, int(time.time() * 1000000))
    return {"user_id": user_id, "strategy": strategy, "count": len(ids)}
