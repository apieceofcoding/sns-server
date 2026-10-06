import math


def recall_at_k(ids, labels, k):
    relevant = {int(i) for i, v in labels.items() if v > 0}
    return len(set(ids[:k]) & relevant) / len(relevant) if relevant else 0.0


def ndcg_at_k(ids, labels, k):
    gains = [labels.get(str(i), 0) for i in ids[:k]]
    dcg = sum((2**v - 1) / math.log2(i + 2) for i, v in enumerate(gains))
    ideal = sorted(labels.values(), reverse=True)[:k]
    idcg = sum((2**v - 1) / math.log2(i + 2) for i, v in enumerate(ideal))
    return dcg / idcg if idcg else 0.0
