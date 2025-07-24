# DeFi Perp Funding Rates Screener - Documentazione Claude

## Panoramica dell'Applicazione

Questa è un'applicazione web che monitora e confronta i funding rates dei mercati perpetual (perp) su diversi exchange decentralizzati (DEX), permettendo di identificare opportunità di arbitraggio attraverso l'analisi automatica degli spread massimi.

## Architettura

### Backend (Python Flask)
- **File principale**: `backend/app.py`
- **Endpoint principale**: `/api/funding-rates`
- **Aggiornamento automatico**: Ogni 3 minuti tramite background thread
- **Cache**: Dati serviti dalla cache, aggiornata automaticamente
- **Gestione errori**: Robusta con fallback e logging

### Frontend (React + TypeScript)
- **Framework**: React con TypeScript, Vite, TailwindCSS
- **File principale**: `frontend/src/pages/Index.tsx`
- **Hook principale**: `frontend/src/hooks/useFundingRates.ts`
- **Componenti**: Tabella, filtri, statistiche
- **Polling**: Controllo ogni 30 secondi per nuovi dati

### Deployment
- **Locale**: Script `start.sh` per avviare backend e frontend
- **Vercel**: API functions in `api/funding-rates.py`
- **Configurazione**: `vercel.json` per routing

## DEX Integrati

### 1. dYdX
- **API**: `https://indexer.dydx.trade/v4/perpetualMarkets`
- **Conversione**: `rate * 24 * 365 * 100` (da hourly a annualizzato %)
- **Formato simboli**: Rimuove `-USD` suffix

### 2. Hyperliquid
- **API**: `https://api.hyperliquid.xyz/info`
- **Payload**: `{"type": "metaAndAssetCtxs"}`
- **Conversione**: `rate * 24 * 365 * 100`
- **Formato simboli**: Usa direttamente il nome

### 3. Paradex
- **API**: `https://api.prod.paradex.trade/v1`
- **Endpoints**: `/markets` + `/markets/summary`
- **Conversione**: `rate * 3 * 365 * 100` (8h funding → annualizzato)
- **Formato simboli**: Rimuove `-USD-PERP` suffix

### 4. Extended Exchange
- **API**: `https://api.extended.exchange/api/v1/info/markets`
- **Conversione**: `rate * 24 * 365 * 100`
- **Formato simboli**: Rimuove `-USD` suffix
- **File test**: `test_extended.py`

## Logica Business

### Calcolo Spread
- **File**: `frontend/src/utils/spreadCalculator.ts`
- **Funzione**: `calculateMaxSpread()` - trova il massimo spread tra tutti i DEX
- **Output**: Spread, DEX high/low, rates high/low

### Filtraggio
- **Spread 0.0**: Automaticamente esclusi (mercati senza opportunità)
- **Minimo 2 DEX**: Solo mercati presenti su almeno 2 exchange
- **Filtri utente**: Arbitraggio, high-spread, low-spread, range personalizzato

### Tipi di Opportunità
1. **Arbitrage**: Segni opposti (positivo/negativo) con spread significativo
2. **High-spread**: Stesso segno ma spread > 100 bps
3. **Low-spread**: Spread minore

## Funzionalità Chiave

### Aggiornamento Automatico
- **Backend**: Thread daemon che aggiorna cache ogni 3 minuti
- **Primo avvio**: Caricamento immediato senza attendere timer
- **Frontend**: Polling ogni 30 secondi per rilevare nuovi dati
- **No controlli manuali**: Utente non può forzare aggiornamenti

### UI/UX
- **Responsive**: Design mobile-first
- **Loading states**: Spinner durante caricamento iniziale
- **Error handling**: Messaggi informativi, no pulsanti retry
- **Real-time indicators**: Timestamp ultimo aggiornamento

### Performance
- **Threading**: Fetch parallelo da tutti i DEX
- **Caching**: Cache di 3 minuti per ridurre chiamate API
- **Filtering**: Client-side per reattività

## File di Configurazione

### Backend
- `requirements.txt`: Dipendenze Python (Flask, requests, flask-cors)
- `runtime.txt`: Versione Python per Vercel

### Frontend
- `package.json`: Dipendenze Node.js
- `vite.config.ts`: Configurazione build
- `tailwind.config.ts`: Styling
- `tsconfig.json`: TypeScript

## Scripts di Test
- `test_dydx.py`: Test isolato dYdX API
- `test_hyperliquid.py`: Test isolato Hyperliquid API  
- `test_paradex.py`: Test isolato Paradex API
- `test_extended.py`: Test isolato Extended Exchange API

## Struttura Dati

### FundingRateData
```typescript
interface FundingRateData {
  market: string;           // "BTC-USD"
  dexRates: DexFundingRate[];
  volume24h: number;        // Placeholder
  openInterest: number;     // Placeholder
  lastUpdate: string;       // ISO timestamp
}

interface DexFundingRate {
  dex: string;             // "dYdX", "Hyperliquid", etc.
  rate: number;            // Annualized percentage
}
```

### API Response
```typescript
interface ApiResponse {
  data: FundingRateData[];
  lastUpdate: string;
  totalMarkets: number;
}
```

## Come Continuare lo Sviluppo

### Nuovi DEX
1. **Creare test file**: `test_new_dex.py`
2. **Implementare funzione**: `get_new_dex_funding_rates()` in `backend/app.py`
3. **Aggiungere al threading**: Modifica `fetch_all_funding_rates()`
4. **Integrare combinazione**: Aggiorna `combine_funding_data()`
5. **Testare**: Verificare formato simboli e conversione rates

### Miglioramenti Prioritari

#### 1. Volume e Open Interest
- Implementare fetch real dei dati volume/OI
- Aggiungere colonne nella tabella
- Filtri per volume minimo

#### 2. Notifiche
- Sistema di alert per opportunità > threshold
- Web push notifications
- Email alerts

#### 3. Storico
- Database per storico funding rates
- Grafici trend temporali
- Analisi pattern storici

#### 4. Performance
- WebSocket per real-time updates
- Service worker per caching
- Background sync

#### 5. Analytics
- Metriche utilizzo
- Tracking opportunità profittevoli
- Dashboard analytics

### Pattern di Sviluppo

#### Aggiungere Filtro
1. Aggiorna `activeFilters` state in `Index.tsx`
2. Modifica `handleFilterChange()` logica
3. Aggiorna UI in `FundingRatesFilters.tsx`

#### Nuovo Endpoint
1. Aggiungi route in `backend/app.py`
2. Crea corrispondente in `api/` per Vercel
3. Aggiorna frontend hook se necessario

#### Nuova Metrica di Spread
1. Implementa calcolo in `spreadCalculator.ts`
2. Aggiorna interfacce TypeScript
3. Modifica rendering tabella

## Environment Variables

### Development
- `NODE_ENV`: 'development' per API localhost
- Backend default: `localhost:5000`

### Production
- API base: '/api' (Vercel functions)
- Build automatico su deploy

## Database Future
Se si vuole aggiungere persistenza:
- **Consigliato**: PostgreSQL su Supabase/Railway
- **Schema**: Markets, FundingRates, Opportunities
- **Indicizzazione**: Timestamp, market, dex
- **Retention**: 30-90 giorni dati storici

## Monitoring
- **Health check**: `/api/health` endpoint
- **Logging**: Console logs per debug
- **Errori**: Graceful handling con fallback

## Testing
- Unit tests per spread calculator
- Integration tests per API endpoints  
- E2E tests per user flows critici

---

*Ultima modifica: Aggiunto Extended Exchange, sistema auto-refresh ogni 3 minuti, rimossi controlli manuali, filtro spread 0.0*