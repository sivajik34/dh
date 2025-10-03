-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    preferences JSONB DEFAULT '{}',
    tier VARCHAR(50) DEFAULT 'standard',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES user_profiles(user_id),
    status VARCHAR(100),
    items JSONB,
    total DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expected_delivery DATE
);

-- Create refunds table
CREATE TABLE IF NOT EXISTS refunds (
    refund_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) REFERENCES orders(order_id),
    user_id VARCHAR(255) REFERENCES user_profiles(user_id),
    amount DECIMAL(10, 2),
    status VARCHAR(100),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP
);

-- Create escalations table
CREATE TABLE IF NOT EXISTS escalations (
    escalation_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES user_profiles(user_id),
    session_id VARCHAR(255),
    message TEXT,
    context JSONB,
    status VARCHAR(100) DEFAULT 'pending',
    assigned_agent VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    service VARCHAR(100),
    action VARCHAR(100),
    details JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_refunds_user_id ON refunds(user_id);
CREATE INDEX idx_escalations_status ON escalations(status);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);