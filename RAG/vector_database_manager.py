import sys
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from utils import extract_text_from_pdf, load_docs
from llm_manager import LLMManager

# Replace sqlite3 with pysqlite3 if needed
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Load the local .env file which defines OPENAI_API_KEY
_ = load_dotenv(find_dotenv())


class MyVectorDBConnector:
    def __init__(self, collection_name, embedding_fn):
        """Vector database operations object"""

        chroma_client = chromadb.HttpClient(host="localhost", port='8000')  # Docker client mode

        # chroma_client = chromadb.Client(Settings(allow_reset=True))  # In-memory mode
        # # For demonstration purposes; in practice, there's no need to reset each time
        # chroma_client.reset()

        # chroma_client = chromadb.Client(Settings(
        #     allow_reset=False,  # Ensure data is not reset on each startup
        #     chroma_db_impl="sqlite",  # Use SQLite as the database implementation
        #     persist_directory="./data/chroma_data"  # Path for data storage
        # ))

        # chroma_client = chromadb.PersistentClient(path="./data/chroma_data")  # Data is stored on disk using SQLite

        # Create or get a collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name
        )

        # Create a collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents, ids):
        '''Add documents and vectors to the collection'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # Vectors for each document
            documents=documents,  # Original content of the documents
            # ids=[f"id{i}" for i in range(len(documents))]  # ID for each document
            ids=ids
        )

        # If Chroma receives a list of documents, it will automatically tag and embed these documents using the collection's embedding function
        # (if no embedding function was provided when creating the collection, the default is used). Chroma will also store the documents themselves.
        # If a document is too large to be embedded using the selected embedding function, an exception will occur.
        # Each document must have a unique associated ID. Attempting to add the same ID twice will result in an error.
        # An optional list of metadata dictionaries can be provided for each document to store additional information and enable filtering.
        # Alternatively, you can directly provide a list of document-related embeddings, and Chroma will store the associated documents without embedding them itself.
        # collection.add(
        #     embeddings=[[0.1378, ..., 0.235], [0.0217, ..., 0.0032]],
        #     documents=["This is a document", "This is another document"],
        #     metadatas=[{"source": "my_source"}, {"source": "my_source"}],
        #     ids=["id1", "id2"]
        # )
        # Trigger re-calculation of the ANN index (if supported)
        # self._rebuild_index_if_needed()

    # def _rebuild_index_if_needed(self):
    #     # Manually trigger index re-calculation if needed
    #     # This is just an example; the specific implementation depends on the library used
    #     pass

    # def reset_collection(self):
    #     self.chroma_client.reset()  # May need adjustments based on the specific implementation
    #     self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def get_document_by_id(self, document_ids) -> tuple[list[str], list[str]]:
        # results = self.collection.get(ids=[document_id])
        results = self.collection.get(ids=document_ids)
        # return results["documents"][0] if results["documents"] else None
        return results["ids"], results["documents"]

    def search(self, query, top_n):
        '''Search the vector database'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results


if __name__ == "__main__":

    client = OpenAI()

    llm_manager = LLMManager(client, 'text-embedding-ada-002')

    collection_name = "llama2_docs"
    # collection_name = "demo"
    # Create a vector database object and add documents
    vector_db = MyVectorDBConnector(collection_name, llm_manager.get_embeddings_default)

    ids, docs = load_docs()

    # Check if documents exist
    existing_document = vector_db.get_document_by_id(ids)
    # Identify new documents that need vector generation
    new_ids = set(ids) - set(existing_document[0])

    # Preserve order of documents needing vector generation
    add_ids = []
    add_docs = []

    for id, doc in zip(ids, docs):
        if id in new_ids:
            add_ids.append(id)
            add_docs.append(doc)

    if len(add_ids) > 0:
        # # Document does not exist, add new documents
        # # Add only once, add documents to the vector database
        # # Extract text from the specified pages of the PDF
        # paragraphs = extract_text_from_pdf(
        #     "data/llama2.pdf",
        #     page_numbers=[3, 4],
        #     min_line_length=10
        # )
        # vector_db.add_documents(paragraphs)
        vector_db.add_documents(documents=add_docs, ids=add_ids)
        print("Documents have been added" + "\n")
    else:
        print("Documents already exist, no need to add again" + "\n")

    user_query = "How many parameters does LLaMA 2 have?"
    results = vector_db.search(user_query, 2)

    # Print out the results
    for result in results['documents'][0]:
        print(result)


# the output is as following:
# In this work, we develop and release Llama 2, a family of pretrained and fine-tuned LLMs, Llama 2 and Llama
# 2-Chat, at scales up to 70B parameters. On the series of helpfulness and safety benchmarks we tested, Llama 2-Chat
# models generally perform better than existing open-source models. They also appear to be on par with some of the
# closed-source models, at least on the human evaluations we performed (see Figures 1 and 3).
# In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models
# (LLMs) ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned LLMs, called Llama 2-Chat, are
# optimized for dialogue use cases. Our models outperform open-source chat models on most benchmarks we tested, and
# based on our human evaluations for helpfulness and safety, may be a suitable substitute for closedsource models.

