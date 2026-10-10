CREATE TABLE IF NOT EXISTS profiles (
 user_id bigint PRIMARY KEY, generation bigint NOT NULL DEFAULT 0, active_at timestamptz
);
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
