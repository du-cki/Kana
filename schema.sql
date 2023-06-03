CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id BIGINT PRIMARY KEY,
    prefix TEXT NOT NULL,
    disabled_modules TEXT[]
);

CREATE TABLE IF NOT EXISTS logging_activity ( -- in cases of when the user/bot leaves and can't log anymore.
    activity_at TIMESTAMP WITH TIME ZONE NOT NULL,
    activity_type INT NOT NULL, -- this is either `0` (paused) or `1` (resumed)
    user_id BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS username_history (
    user_id BIGINT NOT NULL,
    time_changed TIMESTAMP WITH TIME ZONE NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS avatar_history (
    user_id BIGINT NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    avatar_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS animanga_reminders (
    user_id BIGINT NOT NULL,
    reminder_time TIMESTAMP WITH TIME ZONE NOT NULL,
    animanga_id INT NOT NULL, -- the show ID.
    animanga_name TEXT NOT NULL, -- the show name.
    animanga_part INT, -- the episode/chapter number.
    PRIMARY KEY (user_id, animanga_id) -- don't want any dupes.
);
