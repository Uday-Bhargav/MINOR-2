create extension if not exists "pgcrypto";

create table if not exists crisis_events (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  summary text not null,
  source_url text not null unique,
  category text not null check (category in ('Geopolitical', 'Economic', 'Natural Disaster', 'Energy', 'Health')),
  severity text not null check (severity in ('Low', 'Medium', 'High')),
  event_name text not null,
  location text not null,
  published_at timestamptz not null,
  created_at timestamptz not null default now()
);

create table if not exists sector_predictions (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references crisis_events(id) on delete cascade,
  sector_name text not null,
  direction text not null check (direction in ('rise', 'fall', 'neutral')),
  confidence integer not null check (confidence between 0 and 100),
  reasoning text not null,
  created_at timestamptz not null default now()
);

create index if not exists crisis_events_published_at_idx on crisis_events (published_at desc);
create index if not exists crisis_events_category_idx on crisis_events (category);
create index if not exists crisis_events_severity_idx on crisis_events (severity);
create index if not exists sector_predictions_event_id_idx on sector_predictions (event_id);
create index if not exists sector_predictions_sector_name_idx on sector_predictions (sector_name);

create index if not exists crisis_events_search_idx
on crisis_events
using gin (to_tsvector('english', title || ' ' || summary || ' ' || category || ' ' || severity || ' ' || location));

