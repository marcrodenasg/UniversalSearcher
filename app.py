from flask import Flask, render_template, request, jsonify
import requests, base64, json
import torch
import random
import os
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
EBAY_APP_ID = os.getenv("EBAY_APP_ID")
EBAY_CERT_ID = os.getenv("EBAY_CERT_ID")

current_ebay_token = None

# Load Data & AI Model (happens at start the script)
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu') # runs localy on computer

with open('datasetp1.json', 'r') as f:
    products = json.load(f)

#start chache logic (this is gonna save images you've seen to reduce memory + speed)
cache_file = 'embeddings.pt'

# Pre-calculate the meaning of the inventory/description
if os.path.exists(cache_file):
    print("Indexing products...")
    product_embeddings = torch.load(cache_file, map_location=torch.device('cpu'))
else: #IF the data is new...
    print("First time index...")
    descriptions = [f"{p['productName']} {p['description']}" for p in products]
    product_embeddings = model.encode(descriptions, convert_to_tensor=True)

    torch.save(product_embeddings, cache_file)
    print("Index saved to embeddings.pt")

# so we dont have to keep pasting in the tokens
def fetch_new_ebay_token():
    # client id and secret
    auth_str = f"{EBAY_APP_ID}:{EBAY_CERT_ID}"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_auth}"
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope/buy.browse.readonly"
    }
    
    res = requests.post(url, headers=headers, data=data)

    if res.status_code != 200:
        print(f"TOKEN FETCH ERROR: {res.status_code} - {res.text}")
        return None
        
    token = res.json().get('access_token')
    print(f"NEW TOKEN FETCHED: {token[:10]}...")
    return token

# EBAY SEARCH FUNCTIONALITY
def get_ebay_results(query):
    prod_token = fetch_new_ebay_token()
    MANUAL_TOKEN = "v^1.1#i^1#p^3#r^0#I^3#f^0#t^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"

    if not prod_token:
        print("Failed to fetch eBay token. Check your App ID and Cert ID.")
        prod_token = MANUAL_TOKEN
    
    try:
        search_url = f"https://api.ebay.com/buy/browse/v1/item_summary/search?q={query}&limit=10"
        headers = {
            "Authorization": f"Bearer {prod_token}",
            "Content-Type": "application/json",
            "X-EBAY-C-MARKETPLACE-ID": "EBAY_US"
        }
        
        res = requests.get(search_url, headers=headers)
        
        # ERROR CHECK
        if res.status_code == 403 and prod_token != MANUAL_TOKEN:
            print("Automatic token got a 403. Retrying with Manual Token...")
            headers["Authorization"] = f"Bearer {MANUAL_TOKEN}"
            res = requests.get(search_url, headers=headers)

        print(f"EBAY STATUS: {res.status_code}")

        if res.status_code != 200:
            print(f"eBay Error Message: {res.text}")
            return []

        data = res.json()
        items = data.get('itemSummaries', [])
        
        translated = []
        for item in items:
            img_data = item.get('image', {})
            img_url = img_data.get('imageUrl', 'https://via.placeholder.com/300')
            
            translated.append({
                "productName": item.get('title'),
                "brandName": "eBay Find",
                "price": item.get('price', {}).get('value'),
                "imageUrl": img_url,
                "productUrl": item.get('itemWebUrl'),
                "Shop": "ebay",
                "score": "LIVE"
            })
            
        return translated

    except Exception as e:
        print(f"eBay Exception: {e}")
        return []

@app.route('/')
def index(): 
    shuffled_products = list(products) #randomizes iniral feed
    random.shuffle(shuffled_products)

    return render_template('home.html', products=shuffled_products)

@app.route('/search', methods=['POST'])
def ai_search():
    print("--- SEARCH START ---")
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify(products[:50]) #only return a slice

    # Encode the query and compares to inventory
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, product_embeddings)[0]
    
    # Get the top 12 most relevant items
    top_results = torch.topk(cos_scores, k=min(10, len(products)))
    
    local_results = []
    for i, score in zip(top_results.indices, top_results.values): # how accurate it feels
        p = products[int(i)].copy()
        # Convert 0.0-1.0 score to a percentage
        p['score'] = int(float(score) * 100) 
        local_results.append(p)

        #live ebay results
    print(f"Calling eBay for: {query}")
    ebay_results = get_ebay_results(query)
    print(f"eBay results received: {len(ebay_results)}")

    combined_results = local_results + ebay_results #puts it together
    random.shuffle(combined_results)
    print(f"Total combined items: {len(combined_results)}")
    print("--- SEARCH END ---")
    return jsonify(combined_results)


if __name__ == '__main__':
    # Render provides the port via an environment variable
    port = int(os.environ.get("PORT", 5001))
    # '0.0.0.0' tells the app to listen to all outside requests, not just 'localhost'
    app.run(host='0.0.0.0', port=port)