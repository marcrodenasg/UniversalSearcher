from flask import Flask, render_template, request, jsonify
import json
import torch
import random
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# 1. Load Data & AI Model (This happens once when you start the script)
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

with open('datasetp1.json', 'r') as f:
    products = json.load(f)

# 2. Pre-calculate the "meaning" of your inventory
print("Indexing products...")
descriptions = [f"{p['productName']} {p['description']}" for p in products]
product_embeddings = model.encode(descriptions, convert_to_tensor=True)

@app.route('/')
def index():
    shuffled_products = list(products)
    random.shuffle(shuffled_products)

    return render_template('home.html', products=shuffled_products)

@app.route('/search', methods=['POST'])
def ai_search():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify(products)

    # Encode the query and compare to inventory
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, product_embeddings)[0]
    
    # Get the top 5 most relevant items
    top_results = torch.topk(cos_scores, k=min(12, len(products)))
    
    # Create a list of the matched products
    results = [products[i] for i in top_results.indices]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)