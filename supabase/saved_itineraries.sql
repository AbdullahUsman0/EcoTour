create table if not exists saved_itineraries (
  id bigint generated always as identity primary key,
  traveler_name text not null,
  route text not null,
  estimated_cost double precision not null,
  budget_fit text not null,
  plan_json text not null,
  created_at timestamptz default now()
);
