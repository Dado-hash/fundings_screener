# Funding Rates Screener

Un'applicazione web completa per monitorare e analizzare i funding rates delle criptovalute su più DEX (Decentralized Exchanges) per identificare opportunità di arbitraggio.

## 🎯 Caratteristiche

- **Dati in tempo reale** da 3 DEX principali:
  - **dYdX**: Funding rates per mercati perpetui
  - **Hyperliquid**: Predicted funding rates
  - **Paradex**: Funding rates per mercati PERP

- **Analisi automatica degli spread** per identificare:
  - Opportunità di arbitraggio (spread > 100 bps)
  - Spread elevati (spread 50-100 bps)
  - Spread bassi (spread < 50 bps)

- **Interface utente moderna** con:
  - Filtri avanzati per spread e tipologie
  - Statistiche aggregate
  - Aggiornamento automatico ogni 5 minuti
  - Visualizzazione tabellare ordinabile

## 🏗️ Architettura

### Backend (Flask)
- **API REST** per servire i dati di funding rates
- **Cache intelligente** (5 minuti) per ottimizzare le performance
- **Fetch parallelo** dai 3 DEX per ridurre la latenza
- **Gestione errori** robusta per API esterne

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

- **Mostra solo opportunità di arbitraggio**: Filtra solo asset con spread > 100 bps
- **Mostra spread elevati**: Asset con spread tra 50-100 bps
- **Mostra spread bassi**: Asset con spread < 50 bps
- **Range spread personalizzato**: Imposta min/max spread manualmente

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
- Cache backend di 5 minuti per ridurre chiamate API
- Fetch parallelo da tutti i DEX
- Aggiornamento automatico frontend ogni 5 minuti
- Lazy loading e ottimizzazioni React

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
├── test_*.py              # Script originali per testing
├── start.sh               # Script di avvio automatico
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

- [ ] Aggiungere più DEX (GMX, Gains Network, ecc.)
- [ ] Implementare WebSocket per dati real-time
- [ ] Aggiungere grafici storici
- [ ] Implementare alert personalizzabili
- [ ] Aggiungere calcolo PnL per strategie
- [ ] Deploy su cloud (AWS/Vercel)

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.