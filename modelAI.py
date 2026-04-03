# RUN THIS SCRIPT TO SEE HOW AI MAPS OUT DATA
# Unnecessary but i think its interesting to look at and understand
# If sample size / database increases it'll do a better job

import torch
import json
import os
import pandas as pd
import plotly.express as px
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer

# Setup Model & Data
model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
with open('datasetp1.json', 'r') as f:
    products = json.load(f)

cache_file = 'embeddings.pt'

# 2. Check if we need to biold the embeddings or just load them
if os.path.exists(cache_file):
    print("Loading existing embeddings...")
    product_embeddings = torch.load(cache_file, map_location=torch.device('cpu'))
else:
    print("No embeddings found. Generating new ones (this happens once)...")
    descriptions = [f"{p['productName']} {p.get('description', '')}" for p in products]
    product_embeddings = model.encode(descriptions, convert_to_tensor=True)
    torch.save(product_embeddings, cache_file)
    print(f"Saved {len(products)} embeddings to {cache_file}")

# Convert to numpy for the visualization library
embeddings_np = product_embeddings.cpu().numpy()

# Squashing dimensions (t-SNE)
print("Squashing dimensions... this might take a minute.")
tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='pca', learning_rate='auto')
vis_dims = tsne.fit_transform(embeddings_np)

# Create the DataFrame
df = pd.DataFrame({
    'x': vis_dims[:, 0],
    'y': vis_dims[:, 1],
    'name': [p['productName'] for p in products]
})

# Plot
fig = px.scatter(df, x='x', y='y', hover_name='name', title='AI Product Clusters')
fig.show()