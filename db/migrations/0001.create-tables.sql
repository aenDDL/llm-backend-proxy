-- yoyo:
-- transactional: true

CREATE TABLE users (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    membership VARCHAR(50),
    expire_on DATE,
    auth_refresh_token TEXT
);

CREATE TABLE app_tokens (
    owner_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    app_refresh_token TEXT
);

CREATE TABLE requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model VARCHAR(100),
    tokens_total INTEGER,
    cost_usd NUMERIC(10, 6)
);