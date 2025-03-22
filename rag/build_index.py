import os
from typing import List, Dict
import json
import pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class TravelIndexBuilder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []
    
    def load_travel_data(self, data_path: str) -> List[Dict]:
        """Load travel data from JSON file."""
        with open(data_path, 'r') as f:
            return json.load(f)
    
    def build_index(self, documents: List[Dict], output_path: str):
        """
        Build FAISS index from travel documents.
        
        Args:
            documents: List of travel-related documents
            output_path: Path to save the index
        """
        # Extract text content from documents
        texts = [doc.get('description', '') for doc in documents]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        # Save index and documents
        self.documents = documents
        self._save_index(output_path)
    
    def _save_index(self, output_path: str):
        """Save the index and documents to disk."""
        # Save FAISS index
        faiss.write_index(self.index, f"{output_path}/index.faiss")
        
        # Save documents
        with open(f"{output_path}/documents.pkl", 'wb') as f:
            pickle.dump(self.documents, f)

def main():
    # Initialize builder
    builder = TravelIndexBuilder()
    
    # Load travel data
    data_path = "data/raw/travel_data.json"
    documents = builder.load_travel_data(data_path)
    
    # Build and save index
    output_path = "data/processed"
    os.makedirs(output_path, exist_ok=True)
    builder.build_index(documents, output_path)

if __name__ == "__main__":
    main() 