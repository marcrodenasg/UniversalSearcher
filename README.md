The Bench is a sophisticated fashion discovery engine that blends a static local archive
(Dotshop, Grailed, Vestiaire) with live market results from eBay. Using Sentence-Transformer
AI understands "vibes" and semantic meaning, moving beyond simple keyword matching to
provide a cohesive, high-end shopping experience

-Semantic Search: Powered by multi-qa-mpnet-base-dot-v1, the engine understands
descriptive queries like "Old Money," "Minimalist," or "Cyberpunk."
-Live eBay Integration: Fetches real-time listings via the eBay Browse API and 
intelligently blends them into the results
-Smart Query Expansion: If a user searches for a "vibe," the AI extracts relevant brands
and categories from the local database to "translate" the search for the eBay API.

-Dynamic Blending: Archive matches and live listings are ranked together using a unified
scoring system, ensuring the most relevant items always appear first

Clone the repository:
git clone https://github.com/marcrodenasg/EBAYSeach.git
cd EBAYSeach

pip install flask requests torch sentence-transformers python-dotenv

sqlite3 fashion.db "UPDATE products SET shop = 'Dotshop' WHERE shop IS NULL OR shop = '';"

python3 app.py
http://127.0.0.1:5001
