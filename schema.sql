CREATE TABLE IF NOT EXISTS prefixes (
    id BIGINT PRIMARY KEY,
    prefix TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS username_history (
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS avatar_history (
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    format TEXT NOT NULL,
    avatar BYTEA NOT NULL
);

CREATE OR REPLACE FUNCTION insert_avy(one BIGINT, two TIMESTAMP WITH TIME ZONE, three TEXT, four BYTEA)
    RETURNS VOID
    LANGUAGE plpgsql
    AS $$
    BEGIN
        IF NOT EXISTS (
            WITH selection AS (
                SELECT avatar FROM avatar_history
                WHERE user_id = one
                ORDER BY time_changed DESC
                LIMIT 1
            )
            SELECT * FROM selection
            WHERE avatar = four
        ) THEN
            INSERT INTO avatar_history (user_id, time_changed, format, avatar)
            VALUES (one, two, three, four);
        END IF;
    END $$; 
