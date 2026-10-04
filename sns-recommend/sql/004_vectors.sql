CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS embedding vector;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS embedding_version bigint;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS embedding_space text;
ALTER TABLE users ADD COLUMN IF NOT EXISTS embedding vector;
ALTER TABLE users ADD COLUMN IF NOT EXISTS embedding_space text;
CREATE TABLE IF NOT EXISTS embedding_cache (
 key text PRIMARY KEY, embedding jsonb NOT NULL
);
