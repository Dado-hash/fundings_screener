-- Migration script to add support for minute-based intervals
-- This adds interval_minutes column and updates the constraints

-- For PostgreSQL
-- ALTER TABLE notification_settings ADD COLUMN interval_minutes INTEGER CHECK (interval_minutes >= 5 AND interval_minutes <= 60);
-- ALTER TABLE notification_settings ALTER COLUMN interval_hours DROP NOT NULL;
-- ALTER TABLE notification_settings ADD CONSTRAINT check_interval CHECK (
--     (interval_hours IS NOT NULL AND interval_minutes IS NULL) OR
--     (interval_hours IS NULL AND interval_minutes IS NOT NULL)
-- );

-- For SQLite (requires recreating the table)
-- Step 1: Create a backup of existing data
CREATE TABLE notification_settings_backup AS SELECT * FROM notification_settings;

-- Step 2: Drop the old table
DROP TABLE notification_settings;

-- Step 3: Create the new table with updated schema
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER REFERENCES telegram_subscriptions(chat_id),
    name TEXT NOT NULL,
    interval_hours INTEGER,
    interval_minutes INTEGER,
    min_spread REAL DEFAULT 0,
    max_spread REAL DEFAULT 500,
    selected_dexes TEXT,
    show_arbitrage_only BOOLEAN DEFAULT 0,
    show_high_spread_only BOOLEAN DEFAULT 0,
    max_results INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT 1,
    last_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (
        (interval_hours IS NOT NULL AND interval_minutes IS NULL) OR
        (interval_hours IS NULL AND interval_minutes IS NOT NULL)
    )
);

-- Step 4: Migrate existing data (all existing alerts will be in hours)
INSERT INTO notification_settings (
    id, chat_id, name, interval_hours, interval_minutes, min_spread, max_spread,
    selected_dexes, show_arbitrage_only, show_high_spread_only, max_results,
    is_active, last_sent, created_at
)
SELECT 
    id, chat_id, name, interval_hours, NULL, min_spread, max_spread,
    selected_dexes, show_arbitrage_only, show_high_spread_only, max_results,
    is_active, last_sent, created_at
FROM notification_settings_backup;

-- Step 5: Drop the backup table
DROP TABLE notification_settings_backup;
