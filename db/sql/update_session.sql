UPDATE app_tokens
SET app_refresh_token = $1
WHERE owner_id = $2