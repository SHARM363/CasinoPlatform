import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config


def get_connection():
    return psycopg2.connect(
        Config.DATABASE_URL,
        cursor_factory=RealDictCursor
    )


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE,
        email VARCHAR(150) UNIQUE,
        password TEXT NOT NULL,
        balance NUMERIC(18,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS deposits (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        amount NUMERIC(18,2) NOT NULL,
        payment_method VARCHAR(20),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS withdrawals (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        amount NUMERIC(18,2) NOT NULL,
        payment_method VARCHAR(20),
        account_number VARCHAR(30),
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS referrals (
        id SERIAL PRIMARY KEY,
        referrer_id INTEGER REFERENCES users(id),
        referred_id INTEGER REFERENCES users(id),
        reward NUMERIC(18,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS admins (
        id SERIAL PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS payment_settings (
        id SERIAL PRIMARY KEY,
        payment_method VARCHAR(20) UNIQUE NOT NULL,
        payment_type VARCHAR(20),
        payment_number VARCHAR(50),
        usdt_network VARCHAR(20),
        usdt_address VARCHAR(150),
        is_active BOOLEAN DEFAULT TRUE,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS bets (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        game VARCHAR(100),
        bet_amount NUMERIC(18,2) NOT NULL,
        result VARCHAR(20),
        win_loss NUMERIC(18,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS account_information (
        id SERIAL PRIMARY KEY,
        user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        real_name TEXT,
        username VARCHAR(100),
        email VARCHAR(150),
        phone VARCHAR(30),
        whatsapp VARCHAR(30),
        submitted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    ALTER TABLE withdrawals
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20),
    ADD COLUMN IF NOT EXISTS account_number VARCHAR(30);
    """)

    cur.execute("""
    ALTER TABLE deposits
    ADD COLUMN IF NOT EXISTS payment_method VARCHAR(20);
    """)

    cur.execute("""
    ALTER TABLE deposits
    ADD COLUMN IF NOT EXISTS transaction_id VARCHAR(100);
    """)

    cur.execute("""
    ALTER TABLE referrals
    ADD COLUMN IF NOT EXISTS deposit_requirement NUMERIC(18,2) DEFAULT 500,
    ADD COLUMN IF NOT EXISTS turnover_requirement NUMERIC(18,2) DEFAULT 3000,
    ADD COLUMN IF NOT EXISTS bonus_paid BOOLEAN DEFAULT FALSE;
    """)
    # =========================
    # SECURITY VERIFICATION
    # =========================

    cur.execute("""
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    """)

    cur.execute("""
    ALTER TABLE account_information
    ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;
    """)

    cur.execute("""
    ALTER TABLE account_information
    ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE;
    """)

    # One phone number = One account
    cur.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS
    unique_verified_phone
    ON account_information (phone)
    WHERE phone IS NOT NULL
      AND phone <> '';
    """)

    # OTP storage
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verification_otps (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        verification_type VARCHAR(20) NOT NULL,
        destination VARCHAR(150) NOT NULL,
        code_hash TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        attempts INTEGER DEFAULT 0,
        verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
