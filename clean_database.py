#!/usr/bin/env python3
"""
Script per pulire il database SQLite
Permette di cancellare selettivamente le righe dalle tabelle
"""

import sqlite3
import os
from datetime import datetime, timedelta

# Path del database
DB_PATH = os.path.join(os.path.dirname(__file__), 'backend', 'fundings_bot.db')

def connect_db():
    """Connessione al database"""
    return sqlite3.connect(DB_PATH)

def show_tables_info():
    """Mostra informazioni sulle tabelle e il numero di righe"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("=== INFORMAZIONI DATABASE ===")
    
    # Lista delle tabelle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"Tabella: {table_name} - Righe: {count}")
        
        # Mostra alcune righe di esempio se esistono
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            # Ottieni i nomi delle colonne
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"  Colonne: {', '.join(columns)}")
            print(f"  Esempio righe: {len(rows)} mostrate")
            for i, row in enumerate(rows, 1):
                print(f"    {i}: {row}")
        print()
    
    conn.close()

def clean_all_data():
    """Cancella TUTTE le righe da TUTTE le tabelle (mantiene la struttura)"""
    conn = connect_db()
    cursor = conn.cursor()
    
    print("⚠️  ATTENZIONE: Stai per cancellare TUTTI i dati!")
    confirm = input("Sei sicuro? Digita 'CONFERMA' per continuare: ")
    
    if confirm != 'CONFERMA':
        print("Operazione annullata.")
        return
    
    try:
        # Lista delle tabelle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"✅ Cancellate tutte le righe da {table_name}")
        
        conn.commit()
        print("✅ Tutti i dati sono stati cancellati!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Errore: {e}")
    finally:
        conn.close()

def clean_old_logs(days=7):
    """Cancella i log delle notifiche più vecchi di X giorni"""
    conn = connect_db()
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    try:
        cursor.execute("DELETE FROM notification_log WHERE sent_at < ?", (cutoff_date,))
        deleted = cursor.rowcount
        conn.commit()
        print(f"✅ Cancellati {deleted} log più vecchi di {days} giorni")
    except Exception as e:
        conn.rollback()
        print(f"❌ Errore: {e}")
    finally:
        conn.close()

def clean_inactive_users():
    """Cancella utenti non attivi e le loro impostazioni"""
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Prima cancella le impostazioni degli utenti non attivi
        cursor.execute("""
            DELETE FROM notification_settings 
            WHERE chat_id IN (
                SELECT chat_id FROM telegram_subscriptions WHERE is_active = 0
            )
        """)
        settings_deleted = cursor.rowcount
        
        # Poi cancella gli utenti non attivi
        cursor.execute("DELETE FROM telegram_subscriptions WHERE is_active = 0")
        users_deleted = cursor.rowcount
        
        conn.commit()
        print(f"✅ Cancellati {users_deleted} utenti non attivi e {settings_deleted} loro impostazioni")
    except Exception as e:
        conn.rollback()
        print(f"❌ Errore: {e}")
    finally:
        conn.close()

def clean_specific_table():
    """Cancella righe da una tabella specifica"""
    conn = connect_db()
    cursor = conn.cursor()
    
    # Mostra tabelle disponibili
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    print("Tabelle disponibili:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    try:
        choice = int(input("Scegli il numero della tabella: ")) - 1
        if 0 <= choice < len(tables):
            table_name = tables[choice]
            
            # Mostra il contenuto della tabella
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\nTabella '{table_name}' contiene {count} righe.")
            
            if count > 0:
                confirm = input(f"Vuoi cancellare TUTTE le righe da '{table_name}'? (sì/no): ")
                if confirm.lower() in ['sì', 'si', 'yes', 'y']:
                    cursor.execute(f"DELETE FROM {table_name}")
                    deleted = cursor.rowcount
                    conn.commit()
                    print(f"✅ Cancellate {deleted} righe da {table_name}")
                else:
                    print("Operazione annullata.")
            else:
                print("La tabella è già vuota.")
        else:
            print("Scelta non valida.")
    except (ValueError, IndexError):
        print("Input non valido.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Errore: {e}")
    finally:
        conn.close()

def main():
    """Menu principale"""
    if not os.path.exists(DB_PATH):
        print(f"❌ Database non trovato: {DB_PATH}")
        return
    
    while True:
        print("\n" + "="*50)
        print("🧹 PULIZIA DATABASE - FUNDINGS SCREENER")
        print("="*50)
        print("1. Mostra informazioni database")
        print("2. Cancella TUTTI i dati (mantiene tabelle)")
        print("3. Cancella log vecchi (>7 giorni)")
        print("4. Cancella utenti non attivi")
        print("5. Cancella da tabella specifica")
        print("0. Esci")
        print("-"*50)
        
        choice = input("Scegli un'opzione (0-5): ").strip()
        
        if choice == '0':
            print("👋 Ciao!")
            break
        elif choice == '1':
            show_tables_info()
        elif choice == '2':
            clean_all_data()
        elif choice == '3':
            clean_old_logs()
        elif choice == '4':
            clean_inactive_users()
        elif choice == '5':
            clean_specific_table()
        else:
            print("❌ Opzione non valida.")
        
        input("\nPremi INVIO per continuare...")

if __name__ == "__main__":
    main()
