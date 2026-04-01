# Using Sentence Transformers to turn data into embeddings
import json
import torch
from sentence_transformers import SentenceTransformer, util

with open('datasetp1.json', 'r') as info:
    products = json.load(info)

# intitialize local Ai model (~80mb)
print("loading model")
model = SentenceTransformer('all-MiniLM-L6-v2')

#name + description for AI context - creates index
print("INDEXING")
descriptions = [f"{p['productName']} {p['description']}" for p in products]
product_embeddings = model.encode(descriptions, convert_to_tensor=True)

print("\n--- AI SEARCH READY ---")
print("Type 'exit' to quit.")

while True:
    query = input("\nWhat are you looking for? ")
    
    if query.lower() == 'exit':
        break
        
    # AI Logic
    query_embedding = model.encode(query, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, product_embeddings)[0]
    
    # Get top 2 matches
    top_results = torch.topk(cos_scores, k=2)
    
    for score, idx in zip(top_results.values, top_results.indices):
        p = products[idx]
        print(f"\n[Match {score:.2f}] {p['productName']}")
        print(f"  Price: ${p['price']}")
        print(f"  Color: {p['colors']}")
        print(f"  Snippet: {p['description'][:80]}...")
        print(f"  Link: {p['productUrl']}")