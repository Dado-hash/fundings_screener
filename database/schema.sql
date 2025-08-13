-- Telegram Bot Database Schema
-- This file contains the complete database schema for the Telegram bot

-- User subscriptions table
CREATE TABLE IF NOT EXISTS telegram_subscriptions (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    user_id BIGINT,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Notification settings table (users can have multiple alerts)
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT REFERENCES telegram_subscriptions(chat_id),
    name VARCHAR(255) NOT NULL,
    interval_hours INTEGER CHECK (interval_hours >= 1 AND interval_hours <= 24),
    interval_minutes INTEGER CHECK (interval_minutes >= 5 AND interval_minutes <= 60),
    min_spread DECIMAL(5,2) DEFAULT 0 CHECK (min_spread >= 0),
    max_spread DECIMAL(5,2) DEFAULT 500 CHECK (max_spread >= min_spread),
    selected_dexes TEXT[], -- PostgreSQL array, JSON string for SQLite
    show_arbitrage_only BOOLEAN DEFAULT FALSE,
    show_high_spread_only BOOLEAN DEFAULT FALSE,
    max_results INTEGER DEFAULT 5 CHECK (max_results > 0 AND max_results <= 10),
    is_active BOOLEAN DEFAULT TRUE,
    last_sent TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_interval CHECK (
        (interval_hours IS NOT NULL AND interval_minutes IS NULL) OR
        (interval_hours IS NULL AND interval_minutes IS NOT NULL)
    )
);

-- Notification log table for tracking sent messages
CREATE TABLE IF NOT EXISTS notification_log (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT,
    setting_id INTEGER REFERENCES notification_settings(id),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    markets_count INTEGER,
    status VARCHAR(50) -- 'sent', 'failed', 'no_data'
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_chat_id ON telegram_subscriptions(chat_id);
CREATE INDEX IF NOT EXISTS idx_settings_chat_id ON notification_settings(chat_id);
CREATE INDEX IF NOT EXISTS idx_settings_active ON notification_settings(is_active);
CREATE INDEX IF NOT EXISTS idx_settings_last_sent ON notification_settings(last_sent);
CREATE INDEX IF NOT EXISTS idx_log_sent_at ON notification_log(sent_at);

-- Sample data for testing (uncomment if needed)
/*
INSERT INTO telegram_subscriptions (chat_id, user_id, username) 
VALUES (123456789, 123456789, 'test_user');

INSERT INTO notification_settings (chat_id, name, interval_hours, min_spread, selected_dexes, show_arbitrage_only)
VALUES (123456789, 'Test Alert', 5, 100, '["dYdX", "Hyperliquid"]', TRUE);
*/