CREATE TABLE IF NOT EXISTS users (
 id bigint PRIMARY KEY, interests text NOT NULL,
 version bigint NOT NULL DEFAULT 1, active_at timestamptz
);
CREATE TABLE IF NOT EXISTS posts (
 id bigint PRIMARY KEY, author_id bigint NOT NULL, body text NOT NULL,
 topic text NOT NULL, likes int NOT NULL DEFAULT 0, version bigint NOT NULL DEFAULT 1,
 created_at timestamptz NOT NULL, deleted boolean NOT NULL DEFAULT false
);
