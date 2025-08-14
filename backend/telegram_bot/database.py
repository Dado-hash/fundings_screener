"""
Database operations for Telegram Bot
"""

import os
import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import json

# Database imports - support both PostgreSQL and SQLite
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

import sqlite3

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, database_url: str):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection string (postgres:// or sqlite://)
        """
        self.database_url = database_url
        self.is_postgres = database_url.startswith('postgresql://') or database_url.startswith('postgres://')
        self.connection = None
        
        if self.is_postgres and not POSTGRES_AVAILABLE:
            raise ValueError("PostgreSQL dependencies not available. Install psycopg2-binary.")
    
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            if self.is_postgres:
                await self._init_postgres()
            else:
                await self._init_sqlite()
            
            await self._create_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connection"""
        self.connection = psycopg2.connect(
            self.database_url,
            cursor_factory=psycopg2.extras.RealDictCursor
        )
        self.connection.autocommit = True
    
    async def _init_sqlite(self):
        """Initialize SQLite connection"""
        # Extract path from sqlite URL
        if self.database_url.startswith('sqlite:///'):
            db_path = self.database_url[10:]  # Remove 'sqlite:///'
        else:
            db_path = 'fundings_bot.db'  # Default
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
    
    async def _create_tables(self):
        """Create all necessary tables"""
        
        if self.is_postgres:
            # PostgreSQL schema
            schema = """
            CREATE TABLE IF NOT EXISTS telegram_subscriptions (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT UNIQUE NOT NULL,
                user_id BIGINT,
                username VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            );
            
            CREATE TABLE IF NOT EXISTS notification_settings (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT REFERENCES telegram_subscriptions(chat_id),
                name VARCHAR(255) NOT NULL,
                interval_hours INTEGER,
                interval_minutes INTEGER,
                min_spread DECIMAL(5,2) DEFAULT 0,
                max_spread DECIMAL(5,2) DEFAULT 500,
                selected_dexes TEXT[],
                show_arbitrage_only BOOLEAN DEFAULT FALSE,
                show_high_spread_only BOOLEAN DEFAULT FALSE,
                max_results INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT TRUE,
                last_sent TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT check_interval CHECK (
                    (interval_hours IS NOT NULL AND interval_minutes IS NULL) OR
                    (interval_hours IS NULL AND interval_minutes IS NOT NULL)
                )
            );
            
            CREATE TABLE IF NOT EXISTS notification_log (
                id SERIAL PRIMARY KEY,
                chat_id BIGINT,
                setting_id INTEGER REFERENCES notification_settings(id),
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                markets_count INTEGER,
                status VARCHAR(50)
            );
            
            -- Access control tables
            CREATE TABLE IF NOT EXISTS dex_referral_programs (
                id SERIAL PRIMARY KEY,
                dex_name VARCHAR(50) NOT NULL UNIQUE,
                referral_code VARCHAR(100) NOT NULL,
                referral_url TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_registrations (
                id SERIAL PRIMARY KEY,
                telegram_chat_id BIGINT REFERENCES telegram_subscriptions(chat_id),
                telegram_username VARCHAR(255),
                wallet_address VARCHAR(100) NOT NULL,
                dex_name VARCHAR(50) NOT NULL,
                access_granted BOOLEAN DEFAULT FALSE,
                access_granted_at TIMESTAMP,
                access_granted_by VARCHAR(100),
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(telegram_chat_id, dex_name)
            );
            
            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_user_registrations_chat_id ON user_registrations(telegram_chat_id);
            CREATE INDEX IF NOT EXISTS idx_user_registrations_access ON user_registrations(access_granted);
            CREATE INDEX IF NOT EXISTS idx_user_registrations_dex ON user_registrations(dex_name);
            
            -- Default referral links removed - managed via admin panel
            """
        else:
            # SQLite schema
            schema = """
            CREATE TABLE IF NOT EXISTS telegram_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                user_id INTEGER,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
            
            CREATE TABLE IF NOT EXISTS notification_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER REFERENCES telegram_subscriptions(chat_id),
                name TEXT NOT NULL,
                interval_hours INTEGER,
                interval_minutes INTEGER,
                min_spread REAL DEFAULT 0,
                max_spread REAL DEFAULT 500,
                selected_dexes TEXT,
                show_arbitrage_only BOOLEAN DEFAULT 0,
                show_high_spread_only BOOLEAN DEFAULT 0,
                max_results INTEGER DEFAULT 5,
                is_active BOOLEAN DEFAULT 1,
                last_sent TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (
                    (interval_hours IS NOT NULL AND interval_minutes IS NULL) OR
                    (interval_hours IS NULL AND interval_minutes IS NOT NULL)
                )
            );
            
            CREATE TABLE IF NOT EXISTS notification_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                setting_id INTEGER REFERENCES notification_settings(id),
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                markets_count INTEGER,
                status TEXT
            );
            
            -- Access control tables
            CREATE TABLE IF NOT EXISTS dex_referral_programs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dex_name TEXT NOT NULL UNIQUE,
                referral_code TEXT NOT NULL,
                referral_url TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS user_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_chat_id INTEGER REFERENCES telegram_subscriptions(chat_id),
                telegram_username TEXT,
                wallet_address TEXT NOT NULL,
                dex_name TEXT NOT NULL,
                access_granted BOOLEAN DEFAULT 0,
                access_granted_at TIMESTAMP,
                access_granted_by TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(telegram_chat_id, dex_name)
            );
            
            -- Indexes for performance
            CREATE INDEX IF NOT EXISTS idx_user_registrations_chat_id ON user_registrations(telegram_chat_id);
            CREATE INDEX IF NOT EXISTS idx_user_registrations_access ON user_registrations(access_granted);
            CREATE INDEX IF NOT EXISTS idx_user_registrations_dex ON user_registrations(dex_name);
            
            -- Default referral links removed - managed via admin panel
            """
        
        cursor = self.connection.cursor()
        cursor.executescript(schema) if not self.is_postgres else cursor.execute(schema)
        cursor.close()
        
        if self.is_postgres:
            self.connection.commit()
    
    async def create_subscription(self, chat_id: int, user_id: int = None, username: str = None) -> bool:
        """Create a new subscription"""
        try:
            cursor = self.connection.cursor()
            
            if self.is_postgres:
                query = """
                INSERT INTO telegram_subscriptions (chat_id, user_id, username)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    username = EXCLUDED.username,
                    is_active = TRUE
                """
            else:
                query = """
                INSERT OR REPLACE INTO telegram_subscriptions (chat_id, user_id, username)
                VALUES (?, ?, ?)
                """
            
            cursor.execute(query, (chat_id, user_id, username))
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Subscription created/updated for chat_id: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            return False
    
    async def create_notification_setting(self, setting_data: Dict[str, Any]) -> Optional[int]:
        """Create a new notification setting"""
        try:
            cursor = self.connection.cursor()
            
            # Convert selected_dexes list to appropriate format
            if self.is_postgres:
                selected_dexes = setting_data['selected_dexes']
                query = """
                INSERT INTO notification_settings 
                (chat_id, name, interval_hours, interval_minutes, min_spread, max_spread, selected_dexes, 
                 show_arbitrage_only, show_high_spread_only, max_results)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
            else:
                selected_dexes = json.dumps(setting_data['selected_dexes'])
                query = """
                INSERT INTO notification_settings 
                (chat_id, name, interval_hours, interval_minutes, min_spread, max_spread, selected_dexes, 
                 show_arbitrage_only, show_high_spread_only, max_results)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
            
            cursor.execute(query, (
                setting_data['chat_id'],
                setting_data['name'],
                setting_data.get('interval_hours'),
                setting_data.get('interval_minutes'),
                setting_data['min_spread'],
                setting_data['max_spread'],
                selected_dexes,
                setting_data['show_arbitrage_only'],
                setting_data['show_high_spread_only'],
                setting_data['max_results']
            ))
            
            if self.is_postgres:
                setting_id = cursor.fetchone()['id']
            else:
                setting_id = cursor.lastrowid
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Notification setting created: {setting_id} for chat_id: {setting_data['chat_id']}")
            return setting_id
            
        except Exception as e:
            logger.error(f"Error creating notification setting: {e}")
            return None
    
    async def get_user_alerts(self, chat_id: int) -> List[Dict[str, Any]]:
        """Get all alerts for a user"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT id, name, interval_hours, interval_minutes, min_spread, max_spread, selected_dexes,
                   show_arbitrage_only, show_high_spread_only, max_results, 
                   last_sent, created_at, is_active
            FROM notification_settings
            WHERE chat_id = %s AND is_active = %s
            ORDER BY created_at DESC
            """ if self.is_postgres else """
            SELECT id, name, interval_hours, interval_minutes, min_spread, max_spread, selected_dexes,
                   show_arbitrage_only, show_high_spread_only, max_results, 
                   last_sent, created_at, is_active
            FROM notification_settings
            WHERE chat_id = ? AND is_active = 1
            ORDER BY created_at DESC
            """
            
            cursor.execute(query, (chat_id, True) if self.is_postgres else (chat_id,))
            
            alerts = []
            for row in cursor.fetchall():
                alert = dict(row)
                
                # Parse selected_dexes for SQLite
                if not self.is_postgres and isinstance(alert['selected_dexes'], str):
                    alert['selected_dexes'] = json.loads(alert['selected_dexes'])
                
                alerts.append(alert)
            
            cursor.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting user alerts: {e}")
            return []
    
    async def delete_alert(self, chat_id: int, alert_id: int) -> bool:
        """Delete (deactivate) an alert"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            UPDATE notification_settings 
            SET is_active = %s 
            WHERE id = %s AND chat_id = %s
            """ if self.is_postgres else """
            UPDATE notification_settings 
            SET is_active = 0 
            WHERE id = ? AND chat_id = ?
            """
            
            cursor.execute(query, (False, alert_id, chat_id) if self.is_postgres else (alert_id, chat_id))
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Alert {alert_id} deactivated for chat_id: {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting alert: {e}")
            return False
    
    async def get_due_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications that are due to be sent"""
        try:
            cursor = self.connection.cursor()
            
            # Get settings where last_sent is null or older than the specified interval
            if self.is_postgres:
                query = """
                SELECT ns.*, ts.chat_id as subscription_chat_id
                FROM notification_settings ns
                JOIN telegram_subscriptions ts ON ns.chat_id = ts.chat_id
                WHERE ns.is_active = %s AND ts.is_active = %s
                AND (ns.last_sent IS NULL OR 
                     (ns.interval_hours IS NOT NULL AND ns.last_sent <= NOW() - INTERVAL '1 hour' * ns.interval_hours) OR
                     (ns.interval_minutes IS NOT NULL AND ns.last_sent <= NOW() - INTERVAL '1 minute' * ns.interval_minutes))
                """
                cursor.execute(query, (True, True))
            else:
                query = """
                SELECT ns.*, ts.chat_id as subscription_chat_id
                FROM notification_settings ns
                JOIN telegram_subscriptions ts ON ns.chat_id = ts.chat_id
                WHERE ns.is_active = 1 AND ts.is_active = 1
                AND (ns.last_sent IS NULL OR 
                     (ns.interval_hours IS NOT NULL AND datetime(ns.last_sent) <= datetime('now', '-' || ns.interval_hours || ' hours')) OR
                     (ns.interval_minutes IS NOT NULL AND datetime(ns.last_sent) <= datetime('now', '-' || ns.interval_minutes || ' minutes')))
                """
                cursor.execute(query)
            
            notifications = []
            for row in cursor.fetchall():
                notification = dict(row)
                
                # Parse selected_dexes for SQLite
                if not self.is_postgres and isinstance(notification['selected_dexes'], str):
                    notification['selected_dexes'] = json.loads(notification['selected_dexes'])
                
                notifications.append(notification)
            
            cursor.close()
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting due notifications: {e}")
            return []
    
    async def update_last_sent(self, setting_id: int) -> bool:
        """Update last_sent timestamp for a notification setting"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            UPDATE notification_settings 
            SET last_sent = %s 
            WHERE id = %s
            """ if self.is_postgres else """
            UPDATE notification_settings 
            SET last_sent = CURRENT_TIMESTAMP 
            WHERE id = ?
            """
            
            if self.is_postgres:
                cursor.execute(query, (datetime.now(), setting_id))
            else:
                cursor.execute(query, (setting_id,))
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating last_sent: {e}")
            return False
    
    async def log_notification(self, chat_id: int, setting_id: int, markets_count: int, status: str):
        """Log a sent notification"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO notification_log (chat_id, setting_id, markets_count, status)
            VALUES (%s, %s, %s, %s)
            """ if self.is_postgres else """
            INSERT INTO notification_log (chat_id, setting_id, markets_count, status)
            VALUES (?, ?, ?, ?)
            """
            
            cursor.execute(query, (chat_id, setting_id, markets_count, status))
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
                
        except Exception as e:
            logger.error(f"Error logging notification: {e}")
    
    async def check_user_access(self, chat_id: int) -> bool:
        """Check if user has access granted"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT COUNT(*) as access_count
            FROM user_registrations
            WHERE telegram_chat_id = %s AND access_granted = %s
            """ if self.is_postgres else """
            SELECT COUNT(*) as access_count
            FROM user_registrations
            WHERE telegram_chat_id = ? AND access_granted = 1
            """
            
            cursor.execute(query, (chat_id, True) if self.is_postgres else (chat_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result['access_count'] > 0 if result else False
            
        except Exception as e:
            logger.error(f"Error checking user access: {e}")
            return False
    
    async def create_user_registration(self, chat_id: int, username: str, wallet_address: str, dex_name: str) -> Optional[int]:
        """Create new registration"""
        try:
            cursor = self.connection.cursor()
            
            if self.is_postgres:
                query = """
                INSERT INTO user_registrations (telegram_chat_id, telegram_username, wallet_address, dex_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (telegram_chat_id, dex_name) DO UPDATE SET
                    telegram_username = EXCLUDED.telegram_username,
                    wallet_address = EXCLUDED.wallet_address,
                    registration_date = CURRENT_TIMESTAMP
                RETURNING id
                """
            else:
                query = """
                INSERT OR REPLACE INTO user_registrations (telegram_chat_id, telegram_username, wallet_address, dex_name)
                VALUES (?, ?, ?, ?)
                """
            
            cursor.execute(query, (chat_id, username, wallet_address, dex_name))
            
            if self.is_postgres:
                registration_id = cursor.fetchone()['id']
            else:
                registration_id = cursor.lastrowid
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Registration created: {registration_id} for chat_id: {chat_id}, dex: {dex_name}")
            return registration_id
            
        except Exception as e:
            logger.error(f"Error creating user registration: {e}")
            return None
    
    async def get_referral_links(self) -> List[Dict[str, Any]]:
        """Get all active referral programs"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT id, dex_name, referral_code, referral_url, is_active, created_at
            FROM dex_referral_programs
            WHERE is_active = %s
            ORDER BY dex_name
            """ if self.is_postgres else """
            SELECT id, dex_name, referral_code, referral_url, is_active, created_at
            FROM dex_referral_programs
            WHERE is_active = 1
            ORDER BY dex_name
            """
            
            cursor.execute(query, (True,) if self.is_postgres else ())
            
            referrals = []
            for row in cursor.fetchall():
                # Convert to format expected by frontend
                referrals.append({
                    'id': str(row[0]),
                    'name': row[1],  # dex_name -> name
                    'url': row[3],   # referral_url -> url
                    'clicks': 0,     # Default value (not tracked yet)
                    'registrations': 0,  # Default value (not tracked yet)
                    'created_at': row[5] if row[5] else datetime.now().isoformat(),
                    'updated_at': row[5] if row[5] else datetime.now().isoformat(),
                    'is_active': bool(row[4]) if row[4] is not None else True
                })
            
            cursor.close()
            return referrals
            
        except Exception as e:
            logger.error(f"Error getting referral links: {e}")
            return []
    
    async def get_pending_registrations(self) -> List[Dict[str, Any]]:
        """Get all pending registrations for admin dashboard"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT ur.id, ur.telegram_chat_id, ur.telegram_username, ur.wallet_address, 
                   ur.dex_name, ur.registration_date, ur.notes
            FROM user_registrations ur
            WHERE ur.access_granted = %s
            ORDER BY ur.registration_date DESC
            """ if self.is_postgres else """
            SELECT ur.id, ur.telegram_chat_id, ur.telegram_username, ur.wallet_address, 
                   ur.dex_name, ur.registration_date, ur.notes
            FROM user_registrations ur
            WHERE ur.access_granted = 0
            ORDER BY ur.registration_date DESC
            """
            
            cursor.execute(query, (False,) if self.is_postgres else ())
            
            registrations = []
            for row in cursor.fetchall():
                registrations.append(dict(row))
            
            cursor.close()
            return registrations
            
        except Exception as e:
            logger.error(f"Error getting pending registrations: {e}")
            return []
    
    async def approve_user_access(self, registration_id: int, admin_username: str, notes: str = "") -> bool:
        """Approve user access"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            UPDATE user_registrations
            SET access_granted = %s, access_granted_at = %s, access_granted_by = %s, notes = %s
            WHERE id = %s
            """ if self.is_postgres else """
            UPDATE user_registrations
            SET access_granted = 1, access_granted_at = CURRENT_TIMESTAMP, access_granted_by = ?, notes = ?
            WHERE id = ?
            """
            
            if self.is_postgres:
                cursor.execute(query, (True, datetime.now(), admin_username, notes, registration_id))
            else:
                cursor.execute(query, (admin_username, notes, registration_id))
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Registration {registration_id} approved by {admin_username}")
            return True
            
        except Exception as e:
            logger.error(f"Error approving user access: {e}")
            return False
    
    async def get_user_registrations(self, chat_id: int) -> List[Dict[str, Any]]:
        """Get user's registrations"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT ur.id, ur.dex_name, ur.wallet_address, ur.access_granted, 
                   ur.access_granted_at, ur.access_granted_by, ur.registration_date, ur.notes
            FROM user_registrations ur
            WHERE ur.telegram_chat_id = %s
            ORDER BY ur.registration_date DESC
            """ if self.is_postgres else """
            SELECT ur.id, ur.dex_name, ur.wallet_address, ur.access_granted, 
                   ur.access_granted_at, ur.access_granted_by, ur.registration_date, ur.notes
            FROM user_registrations ur
            WHERE ur.telegram_chat_id = ?
            ORDER BY ur.registration_date DESC
            """
            
            cursor.execute(query, (chat_id,))
            
            registrations = []
            for row in cursor.fetchall():
                registrations.append(dict(row))
            
            cursor.close()
            return registrations
            
        except Exception as e:
            logger.error(f"Error getting user registrations: {e}")
            return []
    
    async def get_all_registrations(self) -> List[Dict[str, Any]]:
        """Get all registrations (pending + approved) for admin dashboard"""
        try:
            cursor = self.connection.cursor()
            
            query = """
            SELECT ur.id, ur.telegram_chat_id, ur.telegram_username, ur.wallet_address, 
                   ur.dex_name, ur.access_granted, ur.access_granted_at, ur.access_granted_by,
                   ur.registration_date, ur.notes
            FROM user_registrations ur
            ORDER BY ur.registration_date DESC
            """
            
            cursor.execute(query)
            
            registrations = []
            for row in cursor.fetchall():
                registrations.append(dict(row))
            
            cursor.close()
            return registrations
            
        except Exception as e:
            logger.error(f"Error getting all registrations: {e}")
            return []
    
    async def update_referral_link(self, dex_name: str, referral_code: str, referral_url: str) -> bool:
        """Update referral link for a specific DEX"""
        try:
            cursor = self.connection.cursor()
            
            if self.is_postgres:
                query = """
                INSERT INTO dex_referral_programs (dex_name, referral_code, referral_url)
                VALUES (%s, %s, %s)
                ON CONFLICT (dex_name) DO UPDATE SET
                    referral_code = EXCLUDED.referral_code,
                    referral_url = EXCLUDED.referral_url,
                    created_at = CURRENT_TIMESTAMP
                """
            else:
                query = """
                INSERT OR REPLACE INTO dex_referral_programs (dex_name, referral_code, referral_url)
                VALUES (?, ?, ?)
                """
            
            cursor.execute(query, (dex_name, referral_code, referral_url))
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Referral link updated for {dex_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating referral link: {e}")
            return False

    async def create_referral_link(self, name: str, url: str) -> Optional[Dict[str, Any]]:
        """Create a new referral link"""
        try:
            cursor = self.connection.cursor()
            
            # Generate a default referral code (can be updated later)
            referral_code = f"REF_{name.upper().replace(' ', '_')}"
            
            if self.is_postgres:
                query = """
                INSERT INTO dex_referral_programs (dex_name, referral_code, referral_url)
                VALUES (%s, %s, %s)
                RETURNING id, dex_name, referral_code, referral_url, is_active, created_at
                """
                cursor.execute(query, (name, referral_code, url))
                result = cursor.fetchone()
            else:
                query = """
                INSERT INTO dex_referral_programs (dex_name, referral_code, referral_url)
                VALUES (?, ?, ?)
                """
                cursor.execute(query, (name, referral_code, url))
                
                # Get the inserted record
                cursor.execute("""
                    SELECT id, dex_name, referral_code, referral_url, is_active, created_at
                    FROM dex_referral_programs
                    WHERE rowid = last_insert_rowid()
                """)
                result = cursor.fetchone()
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            if result:
                # Convert to dict format expected by frontend
                return {
                    'id': str(result[0]),
                    'name': result[1],
                    'url': result[3],
                    'clicks': 0,  # Default value
                    'registrations': 0,  # Default value
                    'created_at': result[5] if result[5] else datetime.now().isoformat(),
                    'updated_at': result[5] if result[5] else datetime.now().isoformat(),
                    'is_active': bool(result[4]) if result[4] is not None else True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating referral link: {e}")
            return None

    async def delete_referral_link(self, link_id: str) -> bool:
        """Delete a referral link"""
        try:
            cursor = self.connection.cursor()
            
            if self.is_postgres:
                query = "DELETE FROM dex_referral_programs WHERE id = %s"
            else:
                query = "DELETE FROM dex_referral_programs WHERE id = ?"
            
            cursor.execute(query, (link_id,))
            
            if self.is_postgres:
                deleted_count = cursor.rowcount
            else:
                deleted_count = cursor.rowcount
            
            cursor.close()
            
            if self.is_postgres:
                self.connection.commit()
            else:
                self.connection.commit()
            
            logger.info(f"Referral link {link_id} deleted: {deleted_count > 0}")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting referral link: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")