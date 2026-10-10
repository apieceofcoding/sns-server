ALTER TABLE posts ADD COLUMN IF NOT EXISTS content_version bigint NOT NULL DEFAULT 1;
CREATE TABLE IF NOT EXISTS recommendation_outbox (
 id uuid PRIMARY KEY, event jsonb NOT NULL, delivered_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now()
);
