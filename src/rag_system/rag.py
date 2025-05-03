import re
from typing import List, Dict

class RAGSystem:
    def __init__(self, chunk_size: int = 500):
        self.documents = []
        self.prompts = []
        self.chunks = []
        self.chunk_size = chunk_size

    def add_document(self, document: str):
        self.documents.append(document)
        self.chunks = self._split_into_chunks(document)

    def add_prompt(self, prompt: str):
        self.prompts.append(prompt)

    def _split_into_chunks(self, text: str) -> List[str]:
       
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        if current_chunk:
            chunks.append(current_chunk.strip())
        return chunks

    def retrieve_relevant_chunks(self, query: str, top_k: int = 3) -> List[str]:

        query_words = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []
        for chunk in self.chunks:
            chunk_words = set(re.findall(r'\w+', chunk.lower()))
            score = len(query_words & chunk_words)
            scored_chunks.append((score, chunk))

        relevant = [chunk for score, chunk in sorted(scored_chunks, reverse=True) if score > 0]
        return relevant[:top_k] if relevant else self.chunks[:top_k]  # fallback: first chunks

    def create_rag_structure(self) -> List[Dict[str, str]]:
        rag_structure = []
        for prompt in self.prompts:
            relevant_chunks = self.retrieve_relevant_chunks(prompt)
            for chunk in relevant_chunks:
                rag_structure.append({
                    "prompt": prompt,
                    "document": chunk
                })
        return rag_structure

    def generate_response(self, query: str) -> str:
        relevant_chunks = self.retrieve_relevant_chunks(query)
        if not relevant_chunks:
            return "No relevant documents found."
        response = f"Generated response based on: {relevant_chunks}"
        return response

def create_rag_structure(text: str, prompt: str) -> List[Dict[str, str]]:
    rag = RAGSystem()
    rag.add_document(text)
    rag.add_prompt(prompt)
    return rag.create_rag_structure()