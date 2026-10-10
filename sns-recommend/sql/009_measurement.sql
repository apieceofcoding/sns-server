CREATE TABLE IF NOT EXISTS model_calls (
 id uuid PRIMARY KEY, day date NOT NULL, kind text NOT NULL, model text NOT NULL,
 status text NOT NULL DEFAULT 'started', duration_ms double precision,
 input_tokens int, output_tokens int, estimated_usd double precision,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS generation_runs (
 job_id uuid PRIMARY KEY, mode text NOT NULL, duration_ms double precision,
 strategy text, published boolean, updated_at timestamptz NOT NULL DEFAULT now()
);
