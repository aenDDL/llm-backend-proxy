INSERT INTO app_tokens (owner_id, app_refresh_token)
VALUES ($1, $2)
ON CONFLICT (owner_id)
DO UPDATE SET app_refresh_token = EXCLUDED.app_refresh_token