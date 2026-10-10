CREATE TABLE recommendation_outbox (
 id uuid PRIMARY KEY, event jsonb NOT NULL, delivered_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now()
);
