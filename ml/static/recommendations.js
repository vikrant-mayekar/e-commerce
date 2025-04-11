// Get customer ID from URL
const urlParams = new URLSearchParams(window.location.search);
const customerId = urlParams.get('customer_id');

// Track user interactions
let interactionHistory = {
    views: new Set(),
    clicks: new Set()
};

// Load recommendations and preferences when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadUserPreferences();
    loadRecommendations();
    
    // Setup search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', handleSearch);
    
    // Setup logout button
    document.getElementById('logoutBtn').addEventListener('click', () => {
        window.location.href = '/';
    });
});

// Load and display user preferences
async function loadUserPreferences() {
    try {
        const response = await fetch(`/preferences/${customerId}`);
        if (!response.ok) throw new Error('Failed to load preferences');
        const preferences = await response.json();
        displayUserPreferences(preferences);
    } catch (error) {
        console.error('Error loading preferences:', error);
        const preferencesList = document.getElementById('preferencesList');
        if (preferencesList) {
            preferencesList.innerHTML = '<p>No preferences recorded yet. Start browsing to build your preferences!</p>';
        }
    }
}

function displayUserPreferences(preferences) {
    const preferencesList = document.getElementById('preferencesList');
    if (!preferencesList) return;
    
    preferencesList.innerHTML = '';
    
    if (preferences.length === 0) {
        preferencesList.innerHTML = '<p>No preferences recorded yet. Start browsing to build your preferences!</p>';
        return;
    }
    
    preferences.forEach(pref => {
        const tag = document.createElement('div');
        tag.className = 'preference-tag';
        tag.innerHTML = `
            <span>${pref.category} - ${pref.subcategory}</span>
            <span class="preference-score">${(pref.preference_score * 100).toFixed(0)}%</span>
        `;
        preferencesList.appendChild(tag);
    });
}

// Load and display recommendations
async function loadRecommendations() {
    try {
        const response = await fetch(`/recommend/${customerId}`);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to load recommendations');
        }
        const recommendations = await response.json();
        displayRecommendations(recommendations);
        
        // Track view interactions
        recommendations.forEach(product => {
            if (!interactionHistory.views.has(product.Product_ID)) {
                interactionHistory.views.add(product.Product_ID);
                updateProductInteraction(product.Product_ID, 'view');
            }
        });
    } catch (error) {
        console.error('Error loading recommendations:', error);
        const recommendationsGrid = document.getElementById('recommendationsGrid');
        if (recommendationsGrid) {
            recommendationsGrid.innerHTML = `
                <div class="error-message">
                    <p>Unable to load recommendations at this time. Please try again later.</p>
                    <p>Error: ${error.message}</p>
                </div>
            `;
        }
    }
}

function displayRecommendations(recommendations) {
    const grid = document.getElementById('recommendationsGrid');
    if (!grid) return;
    
    // Sort recommendations by final score in descending order
    recommendations.sort((a, b) => b.Final_Score - a.Final_Score);
    
    grid.innerHTML = '';
    
    recommendations.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <h3>${product.Brand}</h3>
            <p class="category">${product.Category}</p>
            <p class="subcategory">${product.Subcategory}</p>
            <div class="metrics">
                <p class="final-score">Recommendation Score: ${(product.Final_Score * 100).toFixed(1)}%</p>
                <p class="similarity">Similarity: ${(product.Similarity_Score * 100).toFixed(1)}%</p>
                <p class="clicks">Clicks: ${product.Click_Count}</p>
                <p class="views">Views: ${product.View_Count}</p>
            </div>
            <div class="features">
                <p class="rating">Rating: ${product.Product_Rating}</p>
                <p class="sentiment">Sentiment: ${product.Customer_Review_Sentiment_Score}</p>
                <p class="recommendation-score">Recommendation: ${(product.Probability_of_Recommendation * 100).toFixed(2)}%</p>
            </div>
        `;
        
        // Track click interactions
        card.addEventListener('click', () => {
            if (!interactionHistory.clicks.has(product.Product_ID)) {
                interactionHistory.clicks.add(product.Product_ID);
                updateProductInteraction(product.Product_ID, 'click');
            }
        });
        
        grid.appendChild(card);
    });
}

// Handle search functionality
async function handleSearch(e) {
    const query = e.target.value.trim();
    if (query.length < 2) {
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.style.display = 'none';
        }
        return;
    }

    try {
        const response = await fetch(`/search/${customerId}?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to search');
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Error searching:', error);
    }
}

function displaySearchResults(results) {
    const searchResults = document.getElementById('searchResults');
    if (!searchResults) return;
    
    searchResults.innerHTML = '';
    
    results.forEach(product => {
        const result = document.createElement('div');
        result.className = 'search-result';
        result.innerHTML = `
            <h4>${product.Brand}</h4>
            <p>${product.Category} - ${product.Subcategory}</p>
            <p class="rating">Rating: ${product.Product_Rating}</p>
        `;
        result.addEventListener('click', () => {
            document.getElementById('searchInput').value = '';
            searchResults.style.display = 'none';
            displayRecommendations([product]);
        });
        searchResults.appendChild(result);
    });
    
    searchResults.style.display = 'block';
}

// Update product interactions in the database
async function updateProductInteraction(productId, interactionType) {
    try {
        const response = await fetch(`/click/${customerId}/${productId}`, {
            method: 'GET'
        });
        if (!response.ok) throw new Error('Failed to update interaction');
        
        // Reload preferences after interaction
        loadUserPreferences();
    } catch (error) {
        console.error('Error updating interaction:', error);
    }
} 