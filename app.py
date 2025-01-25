import pandas as pd
import numpy as np
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
from collections import defaultdict

# Load Data (Replace paths with actual file paths)
sales_df = pd.read_csv('SALE DATA.csv', skipinitialspace=True)
items_df = pd.read_excel('CATEGORIES DATA.xlsx')

# Preprocess Product Names for Consistency
def clean_name(name):
    return name.strip().lower()

sales_df['Product Name'] = sales_df['Product Name'].apply(clean_name)
items_df['Item'] = items_df['Item'].apply(clean_name)

# Merge Sales Data with Categories
sales_df = sales_df.merge(
    items_df[['Item', 'Category']],
    left_on='Product Name',
    right_on='Item',
    how='left'
).drop(columns=['Item'])

# Calculate Average Price per Product
avg_price = sales_df.groupby('Product Name')['Price'].mean().reset_index()
avg_price.columns = ['Product Name', 'AvgPrice']

# Group Items by Cart (VchNo)
carts = sales_df.groupby('VchNo')['Product Name'].apply(list).reset_index()

# Build Co-occurrence Matrix
co_occurrence = defaultdict(lambda: defaultdict(int))
for cart in carts['Product Name']:
    for i in range(len(cart)):
        for j in range(i+1, len(cart)):
            product_a = cart[i]
            product_b = cart[j]
            co_occurrence[product_a][product_b] += 1
            co_occurrence[product_b][product_a] += 1

# Precompute Product Categories and Prices
product_category = sales_df.dropna(subset=['Category']).set_index('Product Name')['Category'].to_dict()
product_avg_price = avg_price.set_index('Product Name')['AvgPrice'].to_dict()

# Convert co_occurrence to a regular dictionary for pickling
co_occurrence_dict = {k: dict(v) for k, v in co_occurrence.items()}

# Save the ML model (data and structures)
with open('model.pkl', 'wb') as model_file:
    pickle.dump((co_occurrence_dict, product_category, product_avg_price), model_file)

# Flask API with saved model
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

def load_model():
    with open('model.pkl', 'rb') as model_file:
        co_occurrence_dict, product_category, product_avg_price = pickle.load(model_file)
        # Convert back to defaultdict
        co_occurrence = defaultdict(lambda: defaultdict(int), {
            k: defaultdict(int, v) for k, v in co_occurrence_dict.items()
        })
        return co_occurrence, product_category, product_avg_price

co_occurrence, product_category, product_avg_price = load_model()

# Recommendation Logic
def recommend_products(input_product, top_n=5, price_range=0.2):
    input_product = clean_name(input_product)
    
    if input_product not in product_category or input_product not in co_occurrence:
        return []
    
    # Get input product details
    input_category = product_category[input_product]
    input_avg_price = product_avg_price.get(input_product, 0)
    price_low = input_avg_price * (1 - price_range)
    price_high = input_avg_price * (1 + price_range)
    
    # Step 1: Get co-occurring products
    candidates = co_occurrence[input_product]
    candidate_df = pd.DataFrame({
        'Product': list(candidates.keys()),
        'Frequency': list(candidates.values())
    })
    
    # Add category and price
    candidate_df['Category'] = candidate_df['Product'].map(product_category)
    candidate_df['AvgPrice'] = candidate_df['Product'].map(product_avg_price)
    candidate_df = candidate_df.dropna()
    
    # Step 2: Filter by category and price
    same_category = candidate_df[
        (candidate_df['Category'] == input_category) &
        (candidate_df['AvgPrice'].between(price_low, price_high))
    ].sort_values('Frequency', ascending=False)
    
    # Step 3: Fallback 1: Same category, any price
    if len(same_category) < top_n:
        same_category_fallback = candidate_df[
            (candidate_df['Category'] == input_category)
        ].sort_values('Frequency', ascending=False)
        same_category = pd.concat([same_category, same_category_fallback]).drop_duplicates()
    
    # Step 4: Fallback 2: Any category, similar price
    if len(same_category) < top_n:
        price_filtered = candidate_df[
            candidate_df['AvgPrice'].between(price_low, price_high)
        ].sort_values('Frequency', ascending=False)
        same_category = pd.concat([same_category, price_filtered]).drop_duplicates()
    
    # Step 5: Fallback 3: Top in category
    if len(same_category) < top_n:
        top_category = sales_df[sales_df['Category'] == input_category]
        top_products = top_category.groupby('Product Name').size().reset_index(name='Frequency')
        top_products = top_products[top_products['Product Name'] != input_product]
        same_category = pd.concat([same_category, top_products]).drop_duplicates()
    
    # Finalize and return top N
    recommendations = same_category.head(top_n)
    return recommendations[['Product', 'Category', 'AvgPrice', 'Frequency']].to_dict('records')

@app.route('/api/recommend', methods=['GET'])
def get_recommendations():
    input_product = request.args.get('product')
    if not input_product:
        return jsonify({"error": "Product name is required"}), 400

    recommendations = recommend_products(input_product)
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app.run(debug=True)

# Flask API without saved model
app_alt = Flask(__name__)
CORS(app_alt, resources={r"/api/*": {"origins": "http://localhost:5173"}})

@app_alt.route('/api/recommend', methods=['GET'])
def get_recommendations_alt():
    input_product = request.args.get('product')
    if not input_product:
        return jsonify({"error": "Product name is required"}), 400

    recommendations = recommend_products(input_product)
    return jsonify({"recommendations": recommendations})

if __name__ == "__main__":
    app_alt.run(debug=True)