-- Migration SQLite per aggiungere controllo accessi al bot
-- Esegui questo script se usi SQLite

CREATE TABLE IF NOT EXISTS dex_referral_programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dex_name TEXT NOT NULL UNIQUE,
    referral_code TEXT NOT NULL,
    referral_url TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_chat_id INTEGER REFERENCES telegram_subscriptions(chat_id),
    telegram_username TEXT,
    wallet_address TEXT NOT NULL,
    dex_name TEXT NOT NULL,
    access_granted INTEGER DEFAULT 0,
    access_granted_at TIMESTAMP,
    access_granted_by TEXT,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(telegram_chat_id, dex_name)
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_user_registrations_chat_id ON user_registrations(telegram_chat_id);
CREATE INDEX IF NOT EXISTS idx_user_registrations_access ON user_registrations(access_granted);
CREATE INDEX IF NOT EXISTS idx_user_registrations_dex ON user_registrations(dex_name);

-- Inserisci i referral links (modifica con i tuoi veri link)
INSERT OR IGNORE INTO dex_referral_programs (dex_name, referral_code, referral_url) VALUES 
('dydx', 'YOUR_DYDX_REF', 'https://trade.dydx.exchange/?ref=YOUR_DYDX_REF'),
('hyperliquid', 'YOUR_HL_REF', 'https://app.hyperliquid.xyz/join/YOUR_HL_REF'),
('paradex', 'YOUR_PARADEX_REF', 'https://app.paradex.trade/?ref=YOUR_PARADEX_REF');