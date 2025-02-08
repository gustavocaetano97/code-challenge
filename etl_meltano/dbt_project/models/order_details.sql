CREATE TABLE order_details (
    order_id INT REFERENCES orders(order_id),
    product_id INT REFERENCES products(product_id),
    unit_price NUMERIC(10,2) NOT NULL,
    quantity SMALLINT NOT NULL CHECK (quantity > 0),
    discount REAL CHECK (discount BETWEEN 0 AND 1),
    PRIMARY KEY (order_id, product_id)
);
