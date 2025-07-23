# 🚀 Deploy su Vercel

Guida completa per deployare l'app Funding Rates Screener su Vercel.

## 📋 Prerequisiti

1. **Account Vercel**: Registrati su [vercel.com](https://vercel.com)
2. **Repository GitHub**: Il codice deve essere su GitHub
3. **Vercel CLI** (opzionale): `npm i -g vercel`

## 🔧 Deploy Automatico (Raccomandato)

### 1. **Push su GitHub**
```bash
git add .
git commit -m "Setup Vercel deployment"
git push origin main
```

### 2. **Connetti Vercel a GitHub**
1. Vai su [vercel.com/dashboard](https://vercel.com/dashboard)
2. Clicca **"Add New..."** → **"Project"**
3. Importa il repository `fundings_screener`
4. **Non modificare** le impostazioni di build (usa i file di config)
5. Clicca **"Deploy"**

### 3. **URLs Finali**
- **App**: `https://your-project-name.vercel.app`
- **API**: `https://your-project-name.vercel.app/api/funding-rates`

## 🛠️ Deploy Manuale (CLI)

```bash
# Installa Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

## 📁 Struttura File Deploy

Ecco i file che ho creato per il deploy:

```
fundings_screener/
├── vercel.json                 # Config principale Vercel
├── requirements.txt            # Dipendenze Python per serverless
├── api/
│   ├── funding-rates.py       # Serverless function principale
│   └── health.py              # Health check endpoint
└── frontend/
    ├── vercel.json            # Config frontend
    └── src/
        └── hooks/
            └── useFundingRates.ts  # API URLs aggiornate per prod
```

## ⚙️ Configurazioni Importanti

### **Frontend (React + Vite)**
- Build command: `npm run build`
- Output directory: `frontend/dist`
- Framework preset: **Vite**

### **Backend (Python Serverless)**
- Runtime: `python3.9`
- Functions: `/api/funding-rates` e `/api/health`
- CORS: Configurato per tutti i domini

### **API Endpoints in Produzione**
- Health: `https://your-app.vercel.app/api/health`
- Funding Rates: `https://your-app.vercel.app/api/funding-rates`

## 🔍 Test dopo Deploy

1. **Frontend**: Vai all'URL principale
2. **Backend**: Testa `your-app.vercel.app/api/health`
3. **Funzionalità**: Verifica che i dati si caricano

## 🐛 Troubleshooting

### **Errore Build Frontend**
```bash
# Verifica che le dipendenze si installino localmente
cd frontend
npm install
npm run build
```

### **Errore Serverless Functions**
- Controlla che `requirements.txt` sia nella root
- Verifica che Python 3.9 sia specificato in `vercel.json`

### **Errore CORS**
- Headers CORS sono configurati in ogni function
- Se persiste, aggiungi il dominio alle allowed origins

### **Cache non funziona**
- Le serverless functions sono stateless
- La cache è in-memory e dura solo durante l'esecuzione
- Per cache persistente, considera Redis o database

## 🔄 Auto-Deploy

Ogni push su `main` triggerà automaticamente un nuovo deploy su Vercel.

## 💡 Tips Produzione

1. **Limiti Vercel Free**:
   - 100GB bandwidth/mese
   - 10 secondi timeout per function
   - 1000 serverless invocations/giorno

2. **Ottimizzazioni**:
   - Cache implementata (5 minuti)
   - Fetch parallelo dai DEX
   - Error handling robusto

3. **Monitoraggio**:
   - Dashboard Vercel per analytics
   - Function logs in real-time
   - Performance metrics

## ✅ Checklist Deploy

- [ ] Repository pushato su GitHub
- [ ] Vercel collegato al repo
- [ ] Build completato senza errori
- [ ] Frontend carica correttamente
- [ ] API `/api/health` risponde
- [ ] API `/api/funding-rates` ritorna dati
- [ ] Dati si aggiornano automaticamente
- [ ] Filtri funzionano correttamente

🎉 **La tua app è ora live e accessibile globalmente!**