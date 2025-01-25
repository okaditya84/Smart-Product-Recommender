# SmartProductRecommender

## Overview

SmartProductRecommender is a robust recommendation system that leverages purchase history data to provide accurate and relevant product suggestions. It utilizes advanced similarity calculations and dynamic price range adjustments to enhance user shopping experiences.

## Features

- **Data Preprocessing**: Cleans and processes sales and customer data to ensure consistency and accuracy.
- **Purchase Pattern Analysis**: Analyzes purchase patterns to extract meaningful insights such as median quantity, average price, and unique customers.
- **Similarity Calculation**: Calculates product similarity based on price, purchase patterns, and customer overlap.
- **Dynamic Price Range Calculation**: Adapts price ranges dynamically based on product price volatility.
- **Recommendation Generation**: Provides product recommendations based on similarity scores, confidence scores, and fallback mechanisms.
- **API Integration**: Includes a Flask API to serve recommendations based on user input.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/SmartProductRecommender.git
   cd SmartProductRecommender

2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Run the application**:
   ```bash
   python app.py

## Usage

## API Usage

### Get Recommendations
- **Endpoint**: `GET /api/recommend`
- **Description**: Retrieve product recommendations
- **Parameters**:
    - `product` (string): Target product name
- **Example Request**:
    ```http
    GET /api/recommend?product=laptop
    ```
- **Example Response**:
    ```json
    {
  "recommendations": [
    {
      "product": "Product Name",
      "similarity_score": 0.95,
      "avg_price": 100.0,
      "typical_quantity": 10,
      "confidence_score": 0.90
    },
    ...
  ]}

    ```

## Example usage in juypyter notebook

```python
from product_recommendation import ProductRecommender

# Initialize the recommender
recommender = ProductRecommender()
recommender.load_and_process_data('SALE DATA.csv', 'CUSTOMER DATABASE.csv')

# Get recommendations
input_product = "Lux White FlawlessGlow (PO4)41Gm(40*54)"
recommendations = recommender.recommend_products(input_product, price=28.41, quantity=3240)

# Print recommendations
print(f"Recommendations for '{input_product}':")
for idx, rec in enumerate(recommendations, 1):
    print(f"{idx}. {rec['product']} (Avg Price: ₹{rec['avg_price']:.2f}, Typical Quantity: {rec['typical_quantity']})")
```

## Project Structure

- app.py: Flask API implementation to serve recommendations.
- product_recommendation.py: Core recommendation logic and data processing.
- requirements.txt: List of dependencies required to run the project.
- productRecommendation_purchaseHistory.ipynb: Jupyter Notebook for interactive analysis and testing.
