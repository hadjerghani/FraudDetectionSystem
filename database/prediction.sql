CREATE TABLE fraud_predictions (
    prediction_id SERIAL PRIMARY KEY,
    transaction_id INT,
    predicted_label INT,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);