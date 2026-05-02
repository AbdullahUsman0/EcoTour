create table if not exists trip_requests (
  id bigint generated always as identity primary key,
  origin text not null,
  destination text not null,
  budget double precision not null,
  travelers int not null,
  language text not null,
  estimated_distance_km double precision not null,
  estimated_cost double precision not null,
  weather_note text,
  fare_note text,
  created_at timestamptz default now()
);

create table if not exists chat_messages (
  id bigint generated always as identity primary key,
  user_message text not null,
  assistant_message text not null,
  language text not null,
  created_at timestamptz default now()
);
