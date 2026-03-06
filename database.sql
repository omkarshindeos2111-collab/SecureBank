CREATE DATABASE bankdb;
USE bankdb;

-- Customers table
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    account_no VARCHAR(20) UNIQUE,
    balance DECIMAL(10,2)
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    account_no VARCHAR(20),
    amount DECIMAL(10,2),
    type VARCHAR(10),
    date DATE,
    description VARCHAR(255),
    FOREIGN KEY (account_no) REFERENCES customers(account_no)
);

-- Users table for login system
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    account_no VARCHAR(20),
    FOREIGN KEY (account_no) REFERENCES customers(account_no)
);

-- Sample customers
INSERT INTO customers (name, account_no, balance) VALUES
('Kartik Mishra', 'ACC1001', 50000),
('Rahul Patil', 'ACC1002', 72000),
('Sneha Joshi', 'ACC1003', 65000),
('Amit Kulkarni', 'ACC1004', 82000),
('Priya Deshmukh', 'ACC1005', 91000);

-- Sample transactions
INSERT INTO transactions (account_no, amount, type, date, description) VALUES
('ACC1001', 5000, 'debit', '2026-01-05', 'Shopping'),
('ACC1001', 12000, 'debit', '2026-01-15', 'Laptop'),
('ACC1001', 8000, 'credit', '2026-01-20', 'Salary'),

('ACC1002', 10000, 'debit', '2026-01-12', 'Mobile'),

('ACC1003', 15000, 'debit', '2026-02-01', 'Travel'),

('ACC1004', 20000, 'credit', '2026-01-10', 'Freelance'),

('ACC1005', 7000, 'debit', '2026-01-18', 'Groceries');


-- Users login credentials
-- password for all users is: 1234

INSERT INTO users (username, password_hash, account_no) VALUES
('kartik', '$2b$12$KbQi9nJZQzZ8QKJj6TQFJODyXz0zvGqKkG9kP1cFQhPqUQ0ZBqkG2', 'ACC1001'),
('rahul',  '$2b$12$KbQi9nJZQzZ8QKJj6TQFJODyXz0zvGqKkG9kP1cFQhPqUQ0ZBqkG2', 'ACC1002'),
('sneha',  '$2b$12$KbQi9nJZQzZ8QKJj6TQFJODyXz0zvGqKkG9kP1cFQhPqUQ0ZBqkG2', 'ACC1003'),
('amit',   '$2b$12$KbQi9nJZQzZ8QKJj6TQFJODyXz0zvGqKkG9kP1cFQhPqUQ0ZBqkG2', 'ACC1004'),
('priya',  '$2b$12$KbQi9nJZQzZ8QKJj6TQFJODyXz0zvGqKkG9kP1cFQhPqUQ0ZBqkG2', 'ACC1005');
