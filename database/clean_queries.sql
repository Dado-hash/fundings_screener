-- Script SQL per pulire il database
-- Esegui questi comandi con sqlite3 per cancellare specifiche righe

-- ============================================
-- CANCELLARE TUTTI I DATI (mantiene le tabelle)
-- ============================================

-- Cancella tutti i log delle notifiche
-- DELETE FROM notification_log;

-- Cancella tutte le impostazioni di notifica
-- DELETE FROM notification_settings;

-- Cancella tutte le iscrizioni Telegram
-- DELETE FROM telegram_subscriptions;

-- ============================================
-- CANCELLARE DATI SPECIFICI
-- ============================================

-- Cancella log più vecchi di 7 giorni
-- DELETE FROM notification_log 
-- WHERE sent_at < datetime('now', '-7 days');

-- Cancella utenti non attivi e le loro impostazioni
-- DELETE FROM notification_settings 
-- WHERE chat_id IN (
--     SELECT chat_id FROM telegram_subscriptions WHERE is_active = 0
-- );
-- DELETE FROM telegram_subscriptions WHERE is_active = 0;

-- Cancella impostazioni non attive
-- DELETE FROM notification_settings WHERE is_active = 0;

-- Cancella log falliti
-- DELETE FROM notification_log WHERE status = 'failed';

-- ============================================
-- RESET COMPLETO (cancella tutto e ricrea)
-- ============================================

-- DROP TABLE IF EXISTS notification_log;
-- DROP TABLE IF EXISTS notification_settings;
-- DROP TABLE IF EXISTS telegram_subscriptions;

-- Poi ricrea le tabelle eseguendo schema.sql

-- ============================================
-- COMANDI DI VERIFICA
-- ============================================

-- Conta righe per tabella
SELECT 'telegram_subscriptions' as tabella, COUNT(*) as righe FROM telegram_subscriptions
UNION ALL
SELECT 'notification_settings' as tabella, COUNT(*) as righe FROM notification_settings
UNION ALL
SELECT 'notification_log' as tabella, COUNT(*) as righe FROM notification_log;

-- Mostra utenti attivi
-- SELECT * FROM telegram_subscriptions WHERE is_active = 1;

-- Mostra impostazioni attive
-- SELECT * FROM notification_settings WHERE is_active = 1;

-- Mostra log recenti (ultimi 10)
-- SELECT * FROM notification_log ORDER BY sent_at DESC LIMIT 10;
