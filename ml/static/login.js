document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const customerId = document.getElementById('customerId').value;
    
    try {
        const response = await fetch(`http://localhost:5000/login/${customerId}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.status === 'success') {
            window.location.href = `http://localhost:5000/recommendations?customer_id=${customerId}`;
        } else {
            alert('Invalid Customer ID. Please try again.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please make sure the server is running and try again.');
    }
}); 