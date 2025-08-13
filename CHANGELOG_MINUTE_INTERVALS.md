# Aggiunta del supporto per notifiche ogni 5 minuti nel Bot Telegram

## Modifiche implementate

### 1. Schema Database
- **File modificato**: `database/schema.sql`
- **Modifiche**:
  - Aggiunta colonna `interval_minutes` alla tabella `notification_settings`
  - Resa opzionale la colonna `interval_hours` (era NOT NULL)
  - Aggiunto constraint per garantire che sia settato o `interval_hours` o `interval_minutes` ma non entrambi

### 2. Gestori del Bot Telegram
- **File modificato**: `backend/telegram_bot/handlers.py`
- **Modifiche**:
  - Aggiornato il messaggio di setup per includere opzioni di frequenza in minuti (5, 15, 30 minuti)
  - Modificata la funzione `setup_interval()` per accettare input sia in ore che in minuti
  - Supporto per sintassi tipo "5m" per minuti o "5h" per ore
  - Aggiornate le funzioni di visualizzazione alert per mostrare correttamente l'intervallo
  - Modificata la logica di creazione alert per gestire entrambi i tipi di intervallo

### 3. Database Manager
- **File modificato**: `backend/telegram_bot/database.py`
- **Modifiche**:
  - Aggiornato schema di creazione tabelle per supportare nuove colonne
  - Modificata `create_notification_setting()` per gestire intervalli in minuti
  - Aggiornata `get_user_alerts()` per includere la nuova colonna
  - Migliorata `get_due_notifications()` per calcolare scadenze sia per ore che minuti

### 4. Scheduler delle Notifiche
- **File modificato**: `backend/telegram_bot/scheduler.py`
- **Modifiche**:
  - Cambiata frequenza di controllo da ogni 30 minuti a ogni minuto
  - Aggiornata logica di calcolo scadenze notifiche per supportare intervalli in minuti
  - Migliorata gestione del timing per notifiche ad alta frequenza

### 5. Migrazione Database
- **File creato**: `database/migrate_add_minutes_interval.sql`
- **Scopo**: Script per migrare database esistenti al nuovo schema
- **Eseguita**: Migrazione automatica del database SQLite esistente

## Funzionalità aggiunte

### Nuove opzioni di frequenza disponibili:
- **5 minuti**: Per trading molto attivo
- **15 minuti**: Per aggiornamenti frequenti
- **30 minuti**: Per monitoraggio regolare
- **1-24 ore**: Opzioni esistenti mantenute

### Sintassi input supportate:
- `5m` o `5` (per 5 minuti se il numero è 5-60)
- `5h` (per 5 ore)
- `15` (interpretato come minuti se 5-60, ore se 1-24)

### Miglioramenti UX:
- Messaggi di setup più chiari con esempi
- Visualizzazione corretta dell'intervallo negli alert esistenti
- Supporto retrocompatibilità con alert in ore già esistenti

## Test effettuati

✅ Compilazione codice Python senza errori  
✅ Migrazione database completata  
✅ Creazione alert con intervalli in minuti  
✅ Visualizzazione corretta degli alert esistenti  
✅ Compatibilità con alert in ore preesistenti  

## Come utilizzare la nuova funzionalità

1. Avviare il bot con `/setup`
2. Nel passaggio "frequenza", scegliere tra:
   - `5m` per ogni 5 minuti
   - `15m` per ogni 15 minuti  
   - `30m` per ogni 30 minuti
   - `5h` per ogni 5 ore (come prima)
3. Il bot accetterà la sintassi e creerà l'alert con l'intervallo corretto

## Note tecniche

- Lo scheduler ora controlla ogni minuto invece che ogni 30 minuti
- Database constraint garantisce coerenza dei dati
- Supporto completo sia per PostgreSQL che SQLite
- Retrocompatibilità garantita con alert esistenti
