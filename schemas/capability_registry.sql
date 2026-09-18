-- Initial capability registry for PostgreSQL/Supabase.
-- Apply migrations explicitly; registry diffs are proposals, not auto-applied changes.

create table if not exists capabilities (
    id text primary key,
    kind text not null check (kind in ('model', 'agent', 'tool', 'source')),
    provider text,
    domain text,
    status text not null default 'candidate',
    cost_input_usd numeric,
    cost_output_usd numeric,
    latency_ms numeric,
    reliability numeric check (reliability between 0 and 1),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists capability_performance_log (
    id bigserial primary key,
    capability_id text not null references capabilities(id),
    task_class text,
    success boolean not null,
    latency_ms numeric,
    quality_score numeric check (quality_score between 0 and 1),
    estimated_cost_usd numeric,
    evidence jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists registry_diffs (
    id bigserial primary key,
    capability_id text references capabilities(id),
    proposed_change jsonb not null,
    confidence numeric check (confidence between 0 and 1),
    risk_level text not null default 'medium',
    status text not null default 'pending_human_review',
    created_at timestamptz not null default now(),
    reviewed_at timestamptz
);
