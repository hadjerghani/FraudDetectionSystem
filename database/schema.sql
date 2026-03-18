CREATE TABLE IF NOT EXISTS customers (
    customer_id   SERIAL PRIMARY KEY,
    name          VARCHAR(100),
    country       VARCHAR(50),
    account_creation_date DATE,
    risk_score    FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS accounts (
    account_id    SERIAL PRIMARY KEY,
    customer_id   INT REFERENCES customers(customer_id),
    account_type  VARCHAR(50),
    balance       FLOAT,
    status        VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  SERIAL PRIMARY KEY,
    account_id      INT REFERENCES accounts(account_id),
    time_seconds    FLOAT,
    amount          FLOAT,
    fraud_flag      INT DEFAULT 0,
    fraud_prob      FLOAT DEFAULT 0.0,
    v1 FLOAT, v2 FLOAT, v3 FLOAT, v4 FLOAT, v5 FLOAT,
    v6 FLOAT, v7 FLOAT, v8 FLOAT, v9 FLOAT, v10 FLOAT,
    v11 FLOAT, v12 FLOAT, v13 FLOAT, v14 FLOAT,
    v15 FLOAT, v16 FLOAT, v17 FLOAT, v18 FLOAT,
    v19 FLOAT, v20 FLOAT, v21 FLOAT, v22 FLOAT,
    v23 FLOAT, v24 FLOAT, v25 FLOAT, v26 FLOAT,
    v27 FLOAT, v28 FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_transactions_fraud ON transactions(fraud_flag);
CREATE INDEX idx_transactions_amount ON transactions(amount);


