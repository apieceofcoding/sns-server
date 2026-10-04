import json
from pathlib import Path
from statistics import mean
from time import perf_counter

from .config import settings
from .feed import read_feed
from .measurement import metrics


def benchmark(user_id=1, requests=100):
    # Store-path measurement; excludes HTTP, Spring hydration and network between services.
    latencies, ages = [], []
    for _ in range(requests):
        start = perf_counter()
        result = read_feed(user_id)
        latencies.append((perf_counter() - start) * 1000)
        if result.get("ready"):
            from time import time

            ages.append(time() - result["created_at"])
    sorted_ms = sorted(latencies)
    report = {
        "scope": "local Redis read only; not end-to-end SNS latency",
        "mode": settings().model_mode,
        "requests": requests,
        "read_p95_ms": round(sorted_ms[int((requests - 1) * 0.95)], 3),
        "read_mean_ms": round(mean(latencies), 3),
        "cache_hit_rate": len(ages) / requests,
        "mean_list_age_seconds": round(mean(ages), 3) if ages else None,
        **metrics(),
    }
    Path("reports").mkdir(exist_ok=True)
    Path("reports/benchmark.json").write_text(
        json.dumps(report, default=str, ensure_ascii=False, indent=2)
    )
    return report
