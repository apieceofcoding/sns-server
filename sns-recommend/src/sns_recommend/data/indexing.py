from langchain_core.documents import Document

from sns_recommend.core.config import settings
from sns_recommend.providers.embeddings import CachedEmbeddings, space, vector_sql
from sns_recommend.storage.postgres import connection


def index_posts(post_ids=None):
    with connection() as conn:
        if post_ids:
            posts = conn.execute("SELECT * FROM posts WHERE id=ANY(%s)", (post_ids,)).fetchall()
        else:
            posts = conn.execute(
                """SELECT * FROM posts WHERE NOT deleted AND
                (embedding_version IS DISTINCT FROM version OR embedding_space IS DISTINCT FROM %s)
                ORDER BY id""",
                (space(),),
            ).fetchall()
    active = [p for p in posts if not p["deleted"]]
    if settings().model_mode in {"live", "record"}:
        active = active[:20]  # Call again for the next small batch.
    documents = [
        Document(page_content=p["body"], metadata={"id": p["id"], "version": p["version"]})
        for p in active
    ]
    vectors = (
        CachedEmbeddings().embed_documents([d.page_content for d in documents]) if documents else []
    )
    with connection() as conn:
        for post, vector in zip(active, vectors, strict=True):
            conn.execute(
                """UPDATE posts SET embedding=%s::vector,embedding_version=%s,
                embedding_space=%s WHERE id=%s AND version=%s AND NOT deleted""",
                (vector_sql(vector), post["version"], space(), post["id"], post["version"]),
            )
        conn.execute("UPDATE posts SET embedding=NULL,embedding_version=NULL WHERE deleted")
    return {"indexed": len(active), "mode": settings().model_mode, "space": space()}
