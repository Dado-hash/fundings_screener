# Funding Rates Screener

Un'applicazione web completa per monitorare e analizzare i funding rates delle criptovalute su più DEX (Decentralized Exchanges) per identificare opportunità di arbitraggio.

## 🎯 Caratteristiche

- **Dati in tempo reale** da 4 DEX principali:
  - **dYdX**: Funding rates per mercati perpetui
  - **Hyperliquid**: Predicted funding rates
  - **Paradex**: Funding rates per mercati PERP
  - **Extended Exchange**: Funding rates per mercati perpetui

- **Analisi automatica degli spread** per identificare:
  - Opportunità di arbitraggio (spread > 100 bps)
  - Spread elevati (spread 50-100 bps)
  - Spread bassi (spread < 50 bps)

- **Interfaccia utente moderna** con:
  - Filtri avanzati per spread e tipologie
  - Statistiche aggregate
  - Aggiornamento automatico ogni 3 minuti
  - Visualizzazione tabellare ordinabile
  - Esclusione automatica mercati con spread 0.0 bps

## 🏗️ Architettura

### Backend (Flask)
- **API REST** per servire i dati di funding rates
- **Aggiornamento automatico** in background ogni 3 minuti
- **Fetch parallelo** dai 4 DEX per ridurre la latenza
- **Gestione errori** robusta per API esterne
- **Cache intelligente** con background thread per performance ottimali
- **Deployment flessibile**: Locale (Flask) e cloud (Vercel)

### Frontend (React + TypeScript)
- **React 18** con Vite per build veloce
- **TypeScript** per type safety
- **TailwindCSS** per styling
- **Hooks personalizzati** per gestione stato
- **UI components** riutilizzabili con shadcn/ui

## 🚀 Avvio Rapido

### Prerequisiti
- **Python 3.8+**
- **Node.js 16+**
- **npm** o **yarn**

### Installazione e Avvio

1. **Clona il repository**:
   ```bash
   git clone <repo-url>
   cd fundings_screener
   ```

2. **Avvia l'applicazione** (script automatico):
   ```bash
   ./start.sh
   ```

   Questo script:
   - Crea un virtual environment Python
   - Installa le dipendenze backend
   - Installa le dipendenze frontend
   - Avvia backend (porta 5000) e frontend (porta 5173)

3. **Accedi all'applicazione**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000/api/funding-rates

### Avvio Manuale

Se preferisci avviare manualmente:

**Backend:**
```bash
# Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r backend/requirements.txt

# Avvia server
cd backend
python app.py
```

**Frontend:**
```bash
# Installa dipendenze
cd frontend
npm install

# Avvia dev server
npm run dev
```

## 📊 Utilizzo

### Interpretazione dei Dati

- **Rate**: Funding rates annualizzati in percentuale
- **Spread**: Differenza tra il rate più alto e più basso per lo stesso asset
- **Opportunità**: 
  - 🔴 **Arbitraggio** (spread > 100 bps): Opportunità ad alto potenziale
  - 🟡 **High Spread** (50-100 bps): Opportunità moderate  
  - 🟢 **Low Spread** (< 50 bps): Spread contenuti

### Filtri Disponibili

- **Filtro automatico**: Esclude automaticamente mercati con spread 0.0 bps
- **Mostra solo opportunità di arbitraggio**: Filtra solo asset con spread > 100 bps
- **Mostra spread elevati**: Asset con spread tra 50-100 bps
- **Mostra spread bassi**: Asset con spread < 50 bps
- **Range spread personalizzato**: Imposta min/max spread manualmente

### Sistema di Aggiornamento

L'applicazione utilizza un **sistema completamente automatico**:
- **Backend**: Thread in background aggiorna i dati ogni 3 minuti
- **Frontend**: Controlla ogni 30 secondi per nuovi dati disponibili
- **Nessun controllo manuale**: L'utente non può forzare aggiornamenti
- **Zero attesa**: I dati sono sempre disponibili dalla cache

## 🔧 API Endpoints

### GET /api/funding-rates
Restituisce i funding rates di tutti i DEX.

**Response:**
```json
{
  "data": [
    {
      "market": "ETH-USD",
      "dexRates": [
        {"dex": "dYdX", "rate": 45.2},
        {"dex": "Hyperliquid", "rate": 78.5},
        {"dex": "Paradex", "rate": -12.8}
      ],
      "volume24h": 0,
      "openInterest": 0,
      "lastUpdate": "2024-01-15T10:30:00Z"
    }
  ],
  "lastUpdate": "2024-01-15T10:30:00Z",
  "totalMarkets": 25
}
```

### GET /api/health
Health check del backend.

## 🔄 Funzionalità Tecniche

### Caching e Performance
- **Background threading**: Aggiornamento automatico ogni 3 minuti
- **Fetch parallelo** da tutti i 4 DEX simultaneamente
- **Polling frontend** ogni 30 secondi per nuovi dati
- **Cache intelligente**: Dati sempre disponibili, zero attesa per l'utente
- **Lazy loading** e ottimizzazioni React

### Error Handling
- Retry automatico su errori di rete
- Fallback su dati cached in caso di errori
- UI per gestione stati di errore
- Logging dettagliato per debugging

### Sicurezza
- CORS configurato per ambiente di sviluppo
- Validazione input lato client e server
- Timeout su chiamate API esterne
- Sanitizzazione dati in ingresso

## 🛠️ Sviluppo

### Struttura del Progetto
```
fundings_screener/
├── api/
│   └── funding-rates.py    # API Vercel function
├── backend/
│   ├── app.py              # Server Flask principale
│   └── requirements.txt    # Dipendenze Python
├── frontend/
│   ├── src/
│   │   ├── components/     # Componenti React
│   │   ├── hooks/         # Custom hooks
│   │   ├── pages/         # Pagine dell'app
│   │   └── utils/         # Utility functions
│   └── package.json       # Dipendenze Node.js
├── test_*.py              # Script testing per ogni DEX
├── start.sh               # Script di avvio automatico
├── vercel.json            # Configurazione deployment Vercel
├── CLAUDE.md              # Documentazione dettagliata per Claude
└── README.md
```

### Scripts Disponibili

**Frontend:**
- `npm run dev`: Avvia dev server
- `npm run build`: Build per produzione
- `npm run preview`: Preview build di produzione

**Backend:**
- `python app.py`: Avvia server Flask

## 📈 Roadmap

- [x] ✅ **Extended Exchange** integrato
- [x] ✅ **Aggiornamento automatico** ogni 3 minuti
- [x] ✅ **Deploy Vercel** configurato
- [x] ✅ **Filtro spread 0.0** automatico
- [ ] Aggiungere più DEX (GMX, Gains Network, ecc.)
- [ ] Implementare WebSocket per dati real-time
- [ ] Aggiungere grafici storici
- [ ] Implementare alert personalizzabili
- [ ] Aggiungere calcolo PnL per strategie
- [ ] Dati volume e open interest reali

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.