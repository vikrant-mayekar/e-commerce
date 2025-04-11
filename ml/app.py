import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import sqlite3
from django.conf import settings

# File paths from Django settings
CUSTOMER_DATA_FILE = settings.ML_CUSTOMER_DATA
PRODUCT_DATA_FILE = settings.ML_PRODUCT_DATA
DB_PATH = settings.ML_DB_PATH

# Global variables
customer_df = None
product_df = None
tfidf = None
tfidf_matrix = None
features = None
scaler = None

def init_data():
    global customer_df, product_df, tfidf, tfidf_matrix, features, scaler
    
    # Load data
    customer_df = pd.read_csv(CUSTOMER_DATA_FILE)
    product_df = pd.read_csv(PRODUCT_DATA_FILE)
    
    # Features for recommendation
    features = [
        'Product_Rating',
        'Customer_Review_Sentiment_Score',
        'Probability_of_Recommendation'
    ]
    
    # Normalize features
    scaler = MinMaxScaler()
    product_df[features] = scaler.fit_transform(product_df[features])
    
    # Create text representation for search
    product_df['text'] = (
        product_df['Brand'].fillna('') + ' ' +
        product_df['Category'].fillna('') + ' ' +
        product_df['Subcategory'].fillna('')
    )
    
    # Initialize TF-IDF vectorizer for search
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(product_df['text'])

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database and load the data"""
    # Initialize data
    init_data()
    
    # Set up database
    conn = get_db()
    cursor = conn.cursor()
    
    # Create tables for user behavior tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            product_id TEXT,
            interaction_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            category TEXT,
            subcategory TEXT,
            preference_score REAL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product_popularity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT,
            view_count INTEGER DEFAULT 0,
            click_count INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_interactions(customer_id):
    """Get user interactions from the database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, interaction_type, COUNT(*) as count
            FROM user_interactions
            WHERE customer_id = ?
            GROUP BY product_id, interaction_type
        ''', (customer_id,))
        
        interactions = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in interactions]
    except Exception as e:
        print(f"Error getting interactions: {str(e)}")
        return []

def get_preferences(customer_id):
    """Get user preferences from the database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, subcategory, preference_score
            FROM user_preferences
            WHERE customer_id = ?
            ORDER BY preference_score DESC
        ''', (customer_id,))
        
        preferences = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in preferences]
    except Exception as e:
        print(f"Error getting preferences: {str(e)}")
        return []

def get_product_interactions():
    """Get product interaction counts from the database"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, click_count, view_count
            FROM product_popularity
        ''')
        
        popularity_data = cursor.fetchall()
        conn.close()
        
        # Create a dictionary of product interactions
        product_interactions = {}
        for row in popularity_data:
            product_interactions[row['product_id']] = {
                'click_count': row['click_count'],
                'view_count': row['view_count']
            }
        
        return product_interactions
    except Exception as e:
        print(f"Error getting product interactions: {str(e)}")
        return {}

def get_top_recommendations(customer_id, top_n=5):
    """Get personalized recommendations for a user"""
    global customer_df, product_df
    
    if customer_df is None or product_df is None:
        init_data()
    
    try:
        # Get customer preferences
        customer_vector = np.zeros(len(features))
        preference_vector = np.zeros(len(features))
        
        # Add weights from historical data if available
        if customer_id in customer_df['Customer_ID'].values:
            customer_data = customer_df[customer_df['Customer_ID'] == customer_id].iloc[0]
            # Use historical preferences as base weights
            for feature in features:
                if feature in customer_data:
                    customer_vector[features.index(feature)] = customer_data[feature]
        
        # Get user interactions from database
        interactions = get_user_interactions(customer_id)
        
        # Add weights from interactions
        for interaction in interactions:
            product_id = interaction['product_id']
            if product_id in product_df['Product_ID'].values:
                product_data = product_df[product_df['Product_ID'] == product_id].iloc[0]
                weight = 1.0 if interaction['interaction_type'] == 'click' else 0.5
                weight *= interaction['count']
                for feature in features:
                    preference_vector[features.index(feature)] += product_data[feature] * weight
        
        # Get user preferences from database
        preferences = get_preferences(customer_id)
        
        # Add weights from preferences
        for pref in preferences:
            category_mask = product_df['Category'] == pref['category']
            subcategory_mask = product_df['Subcategory'] == pref['subcategory']
            product_mask = category_mask & subcategory_mask
            
            if product_mask.any():
                product_features = product_df.loc[product_mask, features].mean()
                weight = pref['preference_score']
                preference_vector += product_features * weight
        
        # Normalize preference vector
        if np.any(preference_vector):
            preference_vector = preference_vector / np.linalg.norm(preference_vector)
            customer_vector = (customer_vector + preference_vector) / 2
        
        # Calculate recommendations
        if np.any(customer_vector):
            # Calculate similarity scores
            product_features = product_df[features]
            similarity = cosine_similarity(customer_vector.reshape(1, -1), product_features)[0]
        else:
            # If no user data, use default weights
            similarity = np.ones(len(product_df))
        
        product_df['Similarity'] = similarity
        
        # Get click counts for each product
        product_interactions = get_product_interactions()
        
        # Apply popularity boost based on click counts
        max_clicks = max([interactions['click_count'] for interactions in product_interactions.values()], default=1)
        for product_id, interactions in product_interactions.items():
            if product_id in product_df['Product_ID'].values:
                click_boost = 1 + (interactions['click_count'] / max_clicks * 0.2)
                product_df.loc[product_df['Product_ID'] == product_id, 'Similarity'] *= click_boost
        
        # Calculate final recommendation score
        product_df['Final_Score'] = (
            0.4 * product_df['Similarity'] +  # User preferences and interactions
            0.2 * product_df['Product_Rating'] +  # Product quality
            0.2 * product_df['Customer_Review_Sentiment_Score'] +  # Customer satisfaction
            0.2 * product_df['Probability_of_Recommendation']  # Historical recommendation probability
        )
        
        # Ensure final score is between 0 and 1
        product_df['Final_Score'] = product_df['Final_Score'].clip(0, 1)
        
        # Sort by final score in descending order
        top_products = product_df.sort_values(by='Final_Score', ascending=False).head(top_n)
        
        # Convert to list of dictionaries
        recommendations = []
        for _, product in top_products.iterrows():
            recommendations.append({
                'Product_ID': product['Product_ID'],
                'Brand': product['Brand'],
                'Category': product['Category'],
                'Subcategory': product['Subcategory'],
                'Similarity_Score': float(product['Similarity']),
                'Final_Score': float(product['Final_Score'])
            })
        
        return recommendations
    except Exception as e:
        print(f"Error in get_top_recommendations: {str(e)}")
        return []

def update_user_preferences(customer_id, product_data):
    """Update user preferences based on product interaction"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Update or insert preference for category and subcategory
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (customer_id, category, subcategory, preference_score)
            VALUES (?, ?, ?, COALESCE(
                (SELECT preference_score + 0.1 FROM user_preferences 
                WHERE customer_id = ? AND category = ? AND subcategory = ?),
                0.1
            ))
        ''', (
            customer_id, product_data['Category'], product_data['Subcategory'],
            customer_id, product_data['Category'], product_data['Subcategory']
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating preferences: {str(e)}")

def update_product_popularity(product_id, interaction_type):
    """Update product popularity based on user interaction"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Update view or click count
        if interaction_type == 'view':
            cursor.execute('''
                INSERT INTO product_popularity (product_id, view_count)
                VALUES (?, 1)
                ON CONFLICT(product_id) DO UPDATE SET
                view_count = view_count + 1,
                last_updated = CURRENT_TIMESTAMP
            ''', (product_id,))
        elif interaction_type == 'click':
            cursor.execute('''
                INSERT INTO product_popularity (product_id, click_count)
                VALUES (?, 1)
                ON CONFLICT(product_id) DO UPDATE SET
                click_count = click_count + 1,
                last_updated = CURRENT_TIMESTAMP
            ''', (product_id,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error updating product popularity: {str(e)}")

def get_query_recommendations(customer_id, query, top_n=5):
    """Get recommendations based on search query and user preferences"""
    global customer_df, product_df, tfidf, tfidf_matrix
    
    if customer_df is None or product_df is None:
        init_data()
    
    try:
        # Get text similarity
        query_vector = tfidf.transform([query])
        text_sim = cosine_similarity(query_vector, tfidf_matrix)[0]
        product_df['Text_Similarity'] = text_sim
        
        # Get customer preferences
        preferences = get_preferences(customer_id)
        
        # Calculate preference-based score
        preference_score = np.zeros(len(product_df))
        for pref in preferences:
            category_mask = product_df['Category'] == pref['category']
            subcategory_mask = product_df['Subcategory'] == pref['subcategory']
            product_mask = category_mask & subcategory_mask
            preference_score[product_mask] += pref['preference_score']
        
        # Normalize preference score
        if preference_score.max() > 0:
            preference_score = preference_score / preference_score.max()
        
        # Combine text similarity and preference score
        product_df['Combined_Score'] = 0.7 * product_df['Text_Similarity'] + 0.3 * preference_score
        
        # Get top results
        top_results = product_df.sort_values(by='Combined_Score', ascending=False).head(top_n)
        
        # Convert to list of dictionaries
        recommendations = []
        for _, product in top_results.iterrows():
            recommendations.append({
                'Product_ID': product['Product_ID'],
                'Brand': product['Brand'],
                'Category': product['Category'],
                'Subcategory': product['Subcategory'],
                'Text_Similarity': float(product['Text_Similarity']),
                'Combined_Score': float(product['Combined_Score'])
            })
        
        return recommendations
    except Exception as e:
        print(f"Error in get_query_recommendations: {str(e)}")
        return []

def get_popular_products(top_n=10):
    """Get popular products based on view and click counts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT product_id, view_count, click_count
            FROM product_popularity
            ORDER BY (view_count + click_count) DESC
            LIMIT ?
        ''', (top_n,))
        
        popular_products = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        results = []
        for row in popular_products:
            results.append({
                'Product_ID': row['product_id'],
                'View_Count': row['view_count'],
                'Click_Count': row['click_count']
            })
        
        return results
    except Exception as e:
        print(f"Error getting popular products: {str(e)}")
        return []
