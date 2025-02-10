CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(5) REFERENCES customers(customer_id),
    employee_id INT REFERENCES employees(employee_id),
    order_date DATE NOT NULL,
    required_date DATE,
    shipped_date DATE,
    ship_via INT REFERENCES shippers(shipper_id),
    freight NUMERIC(10,2),
    ship_name VARCHAR(40),
    ship_address VARCHAR(60),
    ship_city VARCHAR(15),
    ship_region VARCHAR(15),
    ship_postal_code VARCHAR(10),
    ship_country VARCHAR(15)
);
