from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from rag import DocumentRetriever


class ChatGPT:
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.openai_api_key = openai_api_key
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(self, messages, **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"ChatGPT API error: {str(e)}")

    def get_file_contents(self, file_path, query, top_k=2,**kwargs):
        try:
            embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
            retriever = DocumentRetriever(embeddings)

            results = retriever.retrieve(query, file_path, top_k)

            contents = [doc.page_content for doc in results]
            
            return contents
             
        except Exception as e:
            raise Exception(f"RAG error: {str(e)}")
        
    
    