drop table if exists sessions;
drop table if exists auths;
drop table if exists users;

create table users (
  id           uuid primary key,
  name         text not null,
  avatar_url   text,
  description  text not null default '',
  created_at   timestamptz not null,
  updated_at   timestamptz not null
);

create table auths (
  id               uuid primary key,
  user_id          uuid not null references users (id) on delete cascade,
  provider         text not null check (provider in ('CREDENTIALS', 'GOOGLE')),
  email_encrypted  text not null,
  email_hmac       text not null,
  provider_id      text,
  created_at       timestamptz not null,
  last_login_at    timestamptz,

  check (
    (provider = 'CREDENTIALS' and provider_id is null)
    or
    (provider <> 'CREDENTIALS' and provider_id is not null)
  )
);

create table sessions (
  id               uuid primary key,
  user_id          uuid not null references users (id) on delete cascade,
  token            text not null,
  created_at       timestamptz not null,
  expires_at       timestamptz not null
);

create unique index sessions_user_id_uidx
  on sessions (user_id);

create unique index sessions_token_uidx
  on sessions (token);

create unique index sessions_expires_at_uidx
  on sessions (expires_at);

create unique index auths_user_provider_uidx
  on auths (user_id, provider);

create unique index auths_provider_email_uidx
  on auths (provider, email_hmac);

create unique index auths_oauth_provider_uidx
  on auths (provider, provider_id)
  where provider_id is not null;
