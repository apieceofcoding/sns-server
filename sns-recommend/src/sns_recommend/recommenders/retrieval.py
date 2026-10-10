from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import cast

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from sns_recommend.core.types import Candidate, DatabaseRow, GenerationResult
from sns_recommend.data.events import excluded_ids
from sns_recommend.providers.embeddings import CachedEmbeddings, normalize, space, vector_sql
from sns_recommend.storage.feeds import publish
from sns_recommend.storage.jobs import allocate_generation, enqueue
from sns_recommend.storage.postgres import connection


def update_profile(user_id: int) -> dict[str, int]:
    with connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=%s", (user_id,)).fetchone()
        if not user:
            raise LookupError("unknown user")
        positives = conn.execute(
            """SELECT p.id,p.embedding::text FROM events e
            JOIN posts p ON p.id=e.post_id WHERE e.user_id=%s AND e.kind IN ('like','click')
            AND e.occurred_at<=now() AND e.occurred_at>now()-interval '7 days'
            AND NOT p.deleted AND p.embedding_space=%s AND p.embedding_version=p.version
            GROUP BY p.id ORDER BY max(e.occurred_at) DESC,p.id DESC LIMIT 5""",
            (user_id, space()),
        ).fetchall()
    # Cached initial text vector, plus stored post vectors. No model call per event.
    base = CachedEmbeddings().embed_query(user["interests"])
    vectors = [json.loads(p["embedding"]) for p in positives]
    mixed = (
        normalize(
            [
                0.7 * x + 0.3 * sum(v[i] for v in vectors) / max(1, len(vectors))
                for i, x in enumerate(base)
            ]
        )
        if vectors
        else base
    )
    with connection() as conn:
        conn.execute(
            """UPDATE users SET embedding=%s::vector,embedding_space=%s,
            embedding_version=%s WHERE id=%s AND version=%s""",
            (vector_sql(mixed), space(), user["version"], user_id, user["version"]),
        )
    return {"user_id": user_id, "version": user["version"]}


def retrieve_candidates(
    user_id: int, k: int = 30, as_of: datetime | None = None
) -> list[Candidate]:
    if not 1 <= k <= 50:
        raise ValueError("candidate count must be between 1 and 50")
    reference = as_of or datetime.now(UTC)
    with connection() as conn:
        user = conn.execute("SELECT * FROM users WHERE id=%s", (user_id,)).fetchone()
        if not user:
            raise LookupError("unknown user")
        valid = (
            user["embedding"] is not None
            and user["embedding_space"] == space()
            and user["embedding_version"] == user["version"]
        )
        excluded = excluded_ids(conn, user_id)
        rows = conn.execute(
            """SELECT id,author_id,body,topic,version,created_at,likes,
            CASE WHEN %s AND embedding_space=%s AND embedding_version=version
            THEN 1-(embedding <=> %s::vector) ELSE NULL END AS similarity
            FROM posts WHERE NOT deleted AND author_id<>%s
            AND created_at<=%s AND created_at>=%s""",
            (
                valid,
                space(),
                user["embedding"],
                user_id,
                reference,
                reference - timedelta(hours=48),
            ),
        ).fetchall()
    rows = [r for r in rows if r["id"] not in excluded]
    semantic = sorted(
        [r for r in rows if valid and r["similarity"] is not None],
        key=lambda r: (r["similarity"], r["id"]),
        reverse=True,
    )[:k]
    latest = sorted(rows, key=lambda r: (r["created_at"], r["id"]), reverse=True)[:10]
    popular = sorted(rows, key=lambda r: (r["likes"], r["id"]), reverse=True)[:10]
    merged = {}
    for source, group in [("embedding", semantic), ("latest", latest), ("popular", popular)]:
        for row in group:
            if row["id"] not in merged:
                merged[row["id"]] = {**row, "sources": []}
            merged[row["id"]]["sources"].append(source)
    # Keep fresh and popular candidates even when semantic search already fills k.
    supplement = min(5, k // 3)
    selected: dict[int, DatabaseRow] = {}
    for group in (
        semantic[: k - 2 * supplement],
        latest[:supplement],
        popular[:supplement],
        semantic,
        latest,
        popular,
    ):
        for row in group:
            if len(selected) < k:
                selected[row["id"]] = merged[row["id"]]
    ranked = sorted(
        selected.values(),
        key=lambda r: (r["similarity"] or 0, r["created_at"], r["id"]),
        reverse=True,
    )
    return [cast(Candidate, {**r, "created_at": r["created_at"].isoformat()}) for r in ranked]


class PostRetriever(BaseRetriever):
    user_id: int
    k: int = 30

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list[Document]:
        return [
            Document(page_content=p["body"], metadata={k: v for k, v in p.items() if k != "body"})
            for p in retrieve_candidates(self.user_id, self.k)
        ]


def generate_embedding(user_id: int) -> GenerationResult:
    with connection() as conn:
        generation = allocate_generation(conn, user_id)
    update_profile(user_id)
    docs = PostRetriever(user_id=user_id).invoke("stored user interests")
    ids = [d.metadata["id"] for d in docs]
    with connection() as conn:
        user = conn.execute(
            "SELECT generation FROM users WHERE id=%s FOR UPDATE", (user_id,)
        ).fetchone()
        if user is None:
            raise LookupError("unknown user")
        published = user["generation"] == generation and publish(
            user_id, ids, "embedding", generation
        )
    return {"strategy": "embedding", "post_ids": ids, "published": published}


def process_profile(user_id: int) -> None:
    update_profile(user_id)
    with connection() as conn:
        enqueue(conn, "build", user_id=user_id)
