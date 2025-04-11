# Smart Shopping E-Commerce Platform

A Django-based e-commerce platform with AI-powered product recommendations.

## Features

- User authentication and registration
- Product browsing and details
- Wishlist management
- Purchase history tracking
- AI-powered product recommendations using:
  - Collaborative filtering
  - Content-based filtering
  - Hybrid recommendation system

## Prerequisites

- Python 3.8+
- pip (Python package manager)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ecommerce
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000

## Project Structure

- `users/`: User authentication and profile management
- `products/`: Product management and display
- `recommendations/`: AI-powered recommendation system
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)

## API Endpoints

- `/login/`: User login
- `/register/`: User registration
- `/products/`: List all products
- `/products/<id>/`: Product details
- `/wishlist/`: User's wishlist
- `/purchase-history/`: User's purchase history

## Recommendation System

The recommendation system uses a hybrid approach combining:
1. Collaborative Filtering: Based on user behavior and preferences
2. Content-Based Filtering: Based on product features and descriptions
3. Hybrid Approach: Combines both methods for better recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 