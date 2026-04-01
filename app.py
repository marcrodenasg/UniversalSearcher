from flask import Flask, render_template, request, jsonify
import json
import torch
import random
import os
from sentence_transformers import SentenceTransformer, util

app = Flask(__name__)

# Load Data & AI Model (happens at start the script)
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2') # runs localy on computer

with open('datasetp1.json', 'r') as f:
    products = json.load(f)

#start chache logic (this is gonna save images you've seen to reduce memory + speed)
cache_file = 'embeddings.pt'

# Pre-calculate the meaning of the inventory/description
if os.path.exists(cache_file):
    print("Indexing products...")
    product_embeddings = torch.load(cache_file)
else: #IF the data is new...
    print("First time index...")
    descriptions = [f"{p['productName']} {p['description']}" for p in products]
    product_embeddings = model.encode(descriptions, convert_to_tensor=True)

    torch.save(product_embeddings, cache_file)
    print("Index saved to embeddings.pt")

@app.route('/')
def index(): 
    shuffled_products = list(products) #randomizes iniral feed
    random.shuffle(shuffled_products)

    return render_template('home.html', products=shuffled_products)

@app.route('/search', methods=['POST'])
def ai_search():
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify(products)

    # Encode the query and compares to inventory
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, product_embeddings)[0]
    
    # Get the top 12 most relevant items
    top_results = torch.topk(cos_scores, k=min(12, len(products)))
    
    results = []
    for i, score in zip(top_results.indices, top_results.values): # how accurate it feels
        p = products[int(i)].copy()
        # Convert 0.0-1.0 score to a percentage
        p['score'] = int(float(score) * 100) 
        results.append(p)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)