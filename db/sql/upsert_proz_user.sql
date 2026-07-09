INSERT INTO users (id, name, membership, expire_on, auth_refresh_token)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (id)
DO UPDATE SET
    name = EXCLUDED.name,
    membership = EXCLUDED.membership,
    expire_on = EXCLUDED.expire_on,
    auth_refresh_token = EXCLUDED.auth_refresh_token
