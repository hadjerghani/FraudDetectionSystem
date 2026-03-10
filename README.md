# Financial Fraud Detection System

A **data-driven financial fraud detection system** that combines **database management, machine learning, and web visualization** to identify suspicious financial transactions.

This project simulates a **real banking fraud monitoring environment**, where transactions are stored in a database, analyzed using machine learning models, and displayed through an interactive dashboard.

---

## Project Overview

Financial institutions process **millions of transactions daily**, making manual fraud detection impossible. This project demonstrates how **data engineering, financial analytics, and machine learning** can be combined to detect fraudulent patterns automatically.

The system performs:

- Transaction data storage in a structured database  
- Exploratory data analysis of financial transactions  
- Machine learning-based fraud detection  
- Fraud probability scoring  
- Interactive fraud monitoring dashboard  

---

## Objectives

The main objectives of this project are:

- Design a **financial transactions database**
- Detect **fraudulent behavior using machine learning**
- Analyze **transaction patterns and anomalies**
- Build a **web-based fraud monitoring interface**
- Visualize fraud statistics through a **dashboard**

---

## System Architecture

Transaction Dataset

  ↓

SQL Database

  ↓

Data Processing (Python)

  ↓

Machine Learning Model

  ↓

Fraud Detection Results
  
  ↓

Web Dashboard (HTML / CSS / Flask)


---

## Technologies Used

### Programming
- Python

### Database
- PostgreSQL / MySQL
- SQL

### Data Analysis
- pandas
- numpy
- matplotlib
- seaborn

### Machine Learning
- scikit-learn
- Logistic Regression
- Random Forest
- Anomaly Detection

### Web Development
- Flask
- HTML
- CSS

### Visualization
- Power BI / Chart.js

---

## Database Design

The project uses a **relational database** to store financial transaction data.

### Customers

Stores customer information.

customer_id

name

country

account_creation_date

risk_score


### Accounts

Stores account-level information.

account_id

customer_id

account_type

balance

status


### Transactions

Stores transaction data used for fraud detection.

transaction_id

account_id

date

amount

merchant

merchant_category

location

device

fraud_flag


---

## Machine Learning Model

The fraud detection system uses **supervised machine learning** to classify transactions as:

- Normal transaction
- Fraudulent transaction

Models tested include:

- Logistic Regression
- Decision Trees
- Random Forest

Evaluation metrics include:

- Precision
- Recall
- F1 Score
- Confusion Matrix
- ROC Curve

Due to the **imbalanced nature of fraud datasets**, special attention is given to **recall and precision**.

---

## Dashboard Features

The web interface allows users to monitor fraud activity.

### Fraud Monitoring Dashboard

Displays:

- Total transactions
- Fraudulent transactions detected
- Fraud rate

### Suspicious Transactions

Shows transactions flagged as high risk.

### Transaction Search

Allows users to query a specific transaction and view its fraud probability.

### Fraud Analytics

Visualizes fraud patterns including:

- Fraud by transaction amount
- Fraud by time
- Fraud by location

---

## Project Structure
fraud-detection-system/

data/

transactions.csv

database/

schema.sql

notebooks/

exploratory_analysis.ipynb

model_training.ipynb

src/

fraud_model.py

templates/

dashboard.html

alerts.html

transactions.html

static/

style.css

app.py

README.md


---

## How to Run the Project

### 1. Clone the repository

### 2. Install dependencies

pip install pandas numpy scikit-learn flask matplotlib seaborn


### 3. Run the application

### 4. Open the dashboard


---

## Example Use Cases

This project demonstrates how fraud detection systems can be applied in:

- Banking transaction monitoring
- Credit card fraud detection
- Insurance fraud detection
- Fintech risk monitoring
- Financial crime analytics

---

## Future Improvements

Possible extensions include:

- Real-time transaction streaming
- Deep learning fraud detection models
- Advanced anomaly detection
- Integration with live financial APIs
- Enhanced dashboard visualizations

---

## Author

Developed as part of a **financial mathematics and data science project** combining database systems, machine learning, and financial analytics.

---

⭐ If you find this project useful, consider **starring the repository**.
