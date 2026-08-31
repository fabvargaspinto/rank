-- Registro atómico de public.users + public.auths.
-- Si falla cualquiera de los inserts, se revierte todo.

create unique index if not exists users_name_uidx
  on users (name);

create or replace function public.register_user_with_auth(
  p_user_id uuid,
  p_name text,
  p_avatar_url text,
  p_description text,
  p_user_created_at timestamptz,
  p_user_updated_at timestamptz,
  p_auth_id uuid,
  p_provider text,
  p_email_encrypted text,
  p_email_hmac text,
  p_provider_id text,
  p_auth_created_at timestamptz
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
begin
  if p_provider = 'CREDENTIALS' then
    if p_provider_id is not null then
      raise exception 'INVALID_CREDENTIALS_PROVIDER_ID'
        using errcode = '22023';
    end if;
  elsif p_provider = 'GOOGLE' then
    if p_provider_id is null then
      raise exception 'OAUTH_PROVIDER_ID_REQUIRED'
        using errcode = '22023';
    end if;
  else
    raise exception 'INVALID_AUTH_PROVIDER'
      using errcode = '22023';
  end if;

  insert into public.users (
    id,
    name,
    avatar_url,
    description,
    created_at,
    updated_at
  ) values (
    p_user_id,
    p_name,
    p_avatar_url,
    coalesce(p_description, ''),
    p_user_created_at,
    p_user_updated_at
  );

  insert into public.auths (
    id,
    user_id,
    provider,
    email_encrypted,
    email_hmac,
    provider_id,
    created_at,
    last_login_at
  ) values (
    p_auth_id,
    p_user_id,
    p_provider,
    p_email_encrypted,
    p_email_hmac,
    p_provider_id,
    p_auth_created_at,
    null
  );

  return jsonb_build_object(
    'user_id', p_user_id,
    'auth_id', p_auth_id
  );
exception
  when unique_violation then
    if sqlerrm ilike '%users_name_uidx%' then
      raise exception 'USER_NAME_ALREADY_EXISTS' using errcode = '23505';
    elsif sqlerrm ilike '%auths_provider_email_uidx%' then
      raise exception 'AUTH_EMAIL_ALREADY_EXISTS' using errcode = '23505';
    elsif sqlerrm ilike '%auths_oauth_provider_uidx%' then
      raise exception 'AUTH_OAUTH_ALREADY_EXISTS' using errcode = '23505';
    elsif sqlerrm ilike '%auths_user_provider_uidx%' then
      raise exception 'AUTH_PROVIDER_ALREADY_EXISTS' using errcode = '23505';
    else
      raise;
    end if;
end;
$$;

revoke all on function public.register_user_with_auth(
  uuid, text, text, text, timestamptz, timestamptz,
  uuid, text, text, text, text, timestamptz
) from public;

grant execute on function public.register_user_with_auth(
  uuid, text, text, text, timestamptz, timestamptz,
  uuid, text, text, text, text, timestamptz
) to service_role;
