from elasticsearch import Elasticsearch
import spacy
import torch
from transformers import AutoModel, AutoTokenizer

es = Elasticsearch([{'host': 'https://sapient-api.kupyn.dev/', 'port': 443}])

def insert_vector(index_name, vector_id, vector):
    doc = {"vector": vector}
    es.index(index=index_name, id=vector_id, body=doc)

def search_similar_vectors(index_name, query_vector, num_results=5):
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }

    search_body = {
        "size": num_results,
        "query": script_query,
        "_source": False
    }

    response = es.search(index=index_name, body=search_body)
    return response['hits']['hits']

if __name__ == "__main__":

    index_name = "vector_index"

    sample_vector_id = "1"
    sample_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
    insert_vector(index_name, sample_vector_id, sample_vector)

    query_vector = [0.2, 0.3, 0.4, 0.5, 0.6]
    similar_vectors = search_similar_vectors(index_name, query_vector)

    for hit in similar_vectors:
        print(f"Vector ID: {hit['_id']}, Score: {hit['_score']}")


nlp = spacy.load("en_core_web_sm")

model_name = "bert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def generate_embedding(text):
    input_ids = tokenizer.encode(text, add_special_tokens=True)
    input_ids = torch.tensor(input_ids).unsqueeze(0)

    with torch.no_grad():
        embeddings = model(input_ids)[0]

    return embeddings.mean(dim=1).squeeze().numpy()

input_text = "How can I help you?"
embedding = generate_embedding(input_text)