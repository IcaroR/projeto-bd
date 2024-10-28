-- Create table for users
CREATE TABLE user (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    one_piece BOOLEAN DEFAULT FALSE
);

-- Create table for sellers
CREATE TABLE seller (
    seller_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT NOT NULL,
    one_piece BOOLEAN DEFAULT FALSE
);

-- Create table for products
CREATE TABLE product (
    item_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    seller_id INT NOT NULL,
    fab_at TEXT NOT NULL,
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- Create table for cart
CREATE TABLE cart (
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (item_id) REFERENCES products(item_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (quantity > 0)
);

-- Create table for payments
CREATE TABLE payment (
    payment_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    payment_method VARCHAR(255) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    total_price NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Create a stored procedure to remove old carts
CREATE OR REPLACE FUNCTION remove_old_carts()
RETURNS void AS $$
BEGIN
    INSERT INTO deleted_carts_log (user_id, product_id, quantity, deleted_at)
    SELECT user_id, product_id, quantity, NOW()
    FROM carts
    WHERE created_at < NOW() - INTERVAL '1 month';
    
    DELETE FROM carts
    WHERE created_at < NOW() - INTERVAL '1 month';
END;
$$ LANGUAGE plpgsql;

-- Create the log table for deleted carts
CREATE TABLE deleted_carts_log (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    deleted_at TIMESTAMP NOT NULL
);

-- Create the anayltic views

-- Create the revenue by payment method view
CREATE VIEW revenue_by_payment_method AS
SELECT 
    payment_method,
    COUNT(*) AS number_of_payments,
    SUM(total_price) AS total_revenue
FROM 
    payment
WHERE 
    payment_status = 'completed'
GROUP BY 
    payment_method
ORDER BY 
    total_revenue DESC;

-- Create the payment status distribution view
CREATE VIEW payment_status_distribution AS
SELECT 
    payment_status,
    COUNT(*) AS count,
    SUM(total_price) AS total_revenue
FROM 
    payment
GROUP BY 
    payment_status
ORDER BY 
    count DESC;

-- Create the top users by spending view
CREATE VIEW top_users_by_spending AS
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(p.payment_id) AS number_of_payments,
    SUM(p.total_price) AS total_spent
FROM 
    user u
JOIN 
    payment p ON u.user_id = p.user_id
WHERE 
    p.payment_status = 'completed'
GROUP BY 
    u.user_id, u.name, u.email
ORDER BY 
    total_spent DESC
LIMIT 10;

-- Create the inventory levels view
CREATE VIEW inventory_levels AS
SELECT 
    p.item_id,
    p.name AS product_name,
    s.seller_id,
    s.name AS seller_name,
    p.quantity AS current_stock,
    p.price,
    p.fab_at
FROM 
    product p
JOIN 
    seller s ON p.seller_id = s.seller_id
ORDER BY 
    p.quantity ASC;
