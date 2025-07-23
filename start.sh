#!/bin/bash

# Script per avviare frontend e backend contemporaneamente

echo "🚀 Avvio dell'applicazione Funding Rates Screener..."

# Controlla se Python3 è installato
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato. Installare Python3 per continuare."
    exit 1
fi

# Controlla se Node.js è installato
if ! command -v node &> /dev/null; then
    echo "❌ Node.js non trovato. Installare Node.js per continuare."
    exit 1
fi

# Installa dipendenze backend se non esistono
if [ ! -d "venv" ]; then
    echo "📦 Creazione virtual environment per Python..."
    python3 -m venv venv
fi

echo "📦 Installazione dipendenze backend..."
source venv/bin/activate
pip install -q -r backend/requirements.txt

# Installa dipendenze frontend se non esistono
echo "📦 Installazione dipendenze frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

echo "🔧 Avvio dei servizi..."

# Avvia backend in background
echo "🐍 Avvio backend (porta 5000)..."
source venv/bin/activate
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Attende che il backend si avvii
sleep 3

# Avvia frontend
echo "⚛️  Avvio frontend (porta 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Applicazione avviata con successo!"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:5000/api/funding-rates"
echo ""
echo "Per arrestare l'applicazione, premere Ctrl+C"

# Funzione per arrestare i processi quando lo script viene terminato
cleanup() {
    echo ""
    echo "🛑 Arresto dell'applicazione..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Applicazione arrestata."
    exit 0
}

# Cattura il segnale di interruzione (Ctrl+C)
trap cleanup SIGINT

# Attende che entrambi i processi siano in esecuzione
wait $BACKEND_PID $FRONTEND_PID