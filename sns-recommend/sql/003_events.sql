ALTER TABLE users ADD COLUMN IF NOT EXISTS generation bigint NOT NULL DEFAULT 0;
CREATE TABLE IF NOT EXISTS events (
 event_id uuid PRIMARY KEY, kind text NOT NULL, user_id bigint,
 post_id bigint, occurred_at timestamptz NOT NULL, payload jsonb NOT NULL
);
CREATE TABLE IF NOT EXISTS exclusions (
 user_id bigint NOT NULL, post_id bigint NOT NULL,
 reason text NOT NULL, PRIMARY KEY(user_id,post_id)
);
CREATE TABLE IF NOT EXISTS jobs (
 id uuid PRIMARY KEY, kind text NOT NULL, user_id bigint, post_id bigint,
 generation bigint NOT NULL DEFAULT 0, payload jsonb NOT NULL DEFAULT '{}',
 status text NOT NULL DEFAULT 'pending', attempts int NOT NULL DEFAULT 0,
 available_at timestamptz NOT NULL DEFAULT now(), lease_until timestamptz,
 owner uuid, error text, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS pending_build ON jobs(user_id)
 WHERE kind='build' AND status='pending';
CREATE INDEX IF NOT EXISTS job_claim ON jobs(status,available_at);
CREATE SCHEMA IF NOT EXISTS source_demo;
CREATE TABLE IF NOT EXISTS source_demo.posts (
 id bigint PRIMARY KEY, body text NOT NULL, version bigint NOT NULL
);
CREATE TABLE IF NOT EXISTS source_demo.outbox (
 id uuid PRIMARY KEY, event jsonb NOT NULL, delivered_at timestamptz
);
