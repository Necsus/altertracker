import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app import create_app
from app.models.card import Card
from app.models.card_embedding import CardEmbedding

# MODELE
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# PRE-PROCESS
def generate_effect_embedding(declencheurs, conditions, effets):
    text = ' '.join(declencheurs + conditions + effets)
    embedding = model.encode(text)
    return embedding

def normalize_stat(x, max_value=10):
    return (x or 0) / max_value

def build_full_vector(effect_embedding, main_cost, reserve_cost, forest, mountain, ocean):
    numeric_vector = np.array([
        normalize_stat(main_cost),
        normalize_stat(reserve_cost),
        normalize_stat(forest),
        normalize_stat(mountain),
        normalize_stat(ocean)
    ])
    numeric_vector = numeric_vector * np.array([0.15, 0.10, 0.05, 0.05, 0.05])
    full_vector = np.concatenate([effect_embedding * 0.6, numeric_vector])
    return full_vector

# FULL INDEX BUILD
def build_faiss_index():
    app = create_app()
    with app.app_context():
        embeddings = CardEmbedding.query.all()

        embedding_dim = 384 + 5  # model + numeric
        index = faiss.IndexFlatL2(embedding_dim)
        id_map = []

        for emb in embeddings:
            effect_emb = generate_effect_embedding(
                emb.declencheur, emb.condition, emb.effet
            )
            vector = build_full_vector(
                effect_emb,
                emb.main_cost,
                emb.reserve_cost,
                emb.forest,
                emb.mountain,
                emb.ocean
            )
            index.add(np.array([vector]).astype('float32'))
            id_map.append(emb.card_id)

        faiss.write_index(index, "cards_index.faiss")
        np.save("cards_idmap.npy", np.array(id_map))
        print("Index FAISS construit et sauvegardé ✅")

if __name__ == "__main__":
    build_faiss_index()