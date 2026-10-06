"""Candidate validation and deterministic diversity rules."""


def validate_ranking(candidates, ids):
    expected = [p["id"] for p in candidates]
    if (
        any(type(i) is not int for i in ids)
        or len(ids) != len(expected)
        or set(ids) != set(expected)
    ):
        raise ValueError("ranking must be a permutation of allowed candidate IDs")
    return ids


def diversify(candidates, ids):
    lookup = {p["id"]: p for p in candidates}
    remaining, result = list(ids), []
    while remaining:
        previous = lookup[result[-1]] if result else None
        next_id = next(
            (
                i
                for i in remaining
                if previous is None
                or (
                    lookup[i]["author_id"] != previous["author_id"]
                    and lookup[i]["topic"] != previous["topic"]
                )
            ),
            None,
        )
        if next_id is None:
            next_id = next(
                (
                    i
                    for i in remaining
                    if previous is None or lookup[i]["author_id"] != previous["author_id"]
                ),
                remaining[0],
            )
        result.append(next_id)
        remaining.remove(next_id)
    return result
