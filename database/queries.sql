SELECT COUNT(*) FROM transactions;

SELECT fraud_flag, COUNT(*)
FROM transactions
GROUP BY fraud_flag;

SELECT transaction_id, amount
FROM transactions
WHERE fraud_flag = 1
ORDER BY amount DESC
LIMIT 10;

SELECT fraud_flag , AVG(amount) AS Average_amount
FROM transactions
GROUP BY fraud_flag;

SELECT *
FROM transactions
WHERE amount > 2000;






