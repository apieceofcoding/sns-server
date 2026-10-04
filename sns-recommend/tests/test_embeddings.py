from sns_recommend.embeddings import FixtureEmbeddings, normalize


def test_synthetic_vectors_preserve_topic_and_shape():
    embedding = FixtureEmbeddings()
    a,b,c = embedding.embed_documents(["Python 백엔드", "PostgreSQL FastAPI", "제주 여행"])
    dot = lambda x,y: sum(i*j for i,j in zip(x,y,strict=True))
    assert len(a) == 768
    assert dot(a,b) > dot(a,c)
    assert abs(sum(i*i for i in normalize(a))-1)<1e-6
