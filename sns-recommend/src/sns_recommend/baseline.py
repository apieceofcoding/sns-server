from .feed import publish
from .source import ordered_post_ids


def baseline(user_id, strategy="latest"):
    ids = ordered_post_ids(strategy)
    publish(user_id, ids, strategy)
    return {"user_id": user_id, "strategy": strategy, "count": len(ids)}
