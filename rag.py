import os
from pathlib import Path
import hashlib
from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings

def get_file_hash(file_path: str) -> str:
    """Generate a hash for a file."""
    with open(file_path, "rb") as f:
        file_hash = hashlib.md5()
        for chunk in iter(lambda: f.read(4096), b""):
            file_hash.update(chunk)
    return file_hash.hexdigest()


class DocumentRetriever:
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=['.\n'],
            chunk_size=1500,
            chunk_overlap=50
        )
        Path("embeddings").mkdir(exist_ok=True)

    def get_or_create_embeddings(self, file_path: str) -> FAISS:
        """Get existing embeddings or create new ones for a file."""
        file_hash = get_file_hash(file_path)
        embedding_file = Path("embeddings") / f"{file_hash}.faiss"

        if embedding_file.exists():
            return FAISS.load_local(str(embedding_file), self.embeddings, allow_dangerous_deserialization=True)

        text = Path(file_path).read_text(encoding='utf-8')
        documents = self.text_splitter.create_documents([text])
        vector_db = FAISS.from_documents(documents, self.embeddings)
        vector_db.save_local(str(embedding_file))

        return vector_db

    def retrieve(self, query: str, file_path: str, top_k: int = 1) -> List[Document]:
        """Retrieve relevant documents based on the query."""
        vector_db = self.get_or_create_embeddings(file_path)
        return vector_db.similarity_search(query, k=top_k)


def main():
    api_key = os.getenv('OPENAI_API_KEY')
    embeddings = OpenAIEmbeddings(api_key=api_key)
    retriever = DocumentRetriever(embeddings)

    query = "hello"
    top_k = 2

    file_path = 'E:\Codes\gpt_engineer\example.txt'
    results = retriever.retrieve(query, file_path, top_k)

    
    print([doc.page_content for doc in results])

if __name__ == "__main__":
    main()