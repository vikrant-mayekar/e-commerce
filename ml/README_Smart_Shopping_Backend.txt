
🛍️ Smart Shopping: Personalized E-Commerce Backend (Flask + ML)

This backend powers a multi-agent AI system for hyper-personalized product recommendations in e-commerce. It includes:
- An ML-powered recommender system
- SQLite long-term memory for click tracking
- REST API endpoints for use with a PHP frontend

📦 Prerequisites
1. Python 3.7+
2. Pip (Python package manager)

🔧 Setup Instructions

1. Clone this repository
    git clone https://github.com/your-repo/smart-shopping-backend.git
    cd smart-shopping-backend

2. Install dependencies
    pip install -r requirements.txt

3. Add your CSV datasets
Ensure these files are in the root directory:
- customer_data_collection.csv
- product_recommendation_data.csv

4. Run the Flask server
    python app.py

This will start the server at http://127.0.0.1:5000

🚀 API Endpoints Guide

1. 🔐 Login Endpoint
URL: /login/<customer_id>
Method: GET
Validates if the customer exists.
Example: GET /login/C1000

2. 🎯 Recommendation Endpoint
URL: /recommend/<customer_id>
Method: GET
Returns top product recommendations for a customer.

3. 🔍 Search with Personalization
URL: /search/<customer_id>?query=<search_term>
Method: GET
Returns products relevant to the query and similar users.

4. 🧠 Click Tracking
URL: /click/<customer_id>/<product_id>
Method: GET
Logs a user click into SQLite for long-term memory.

🧠 Architecture Summary

| Agent         | Role                                              |
|---------------|---------------------------------------------------|
| Customer Agent| Builds a profile based on behavior and metadata  |
| Product Agent | Processes product features and sentiment         |
| Recommender   | Matches customers with best-fit products         |
| Memory Agent  | Logs interactions into SQLite for future learning|

📁 Folder Structure

smart-shopping-backend/
├── app.py
├── feedback.db
├── customer_data_collection.csv
├── product_recommendation_data.csv
├── requirements.txt
└── README.txt
