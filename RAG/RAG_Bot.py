from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from llm_manager import LLMManager
from vector_database_manager import MyVectorDBConnector
from utils import prompt_template

# Load the local .env file which defines OPENAI_API_KEY
_ = load_dotenv(find_dotenv())


class RAG_Bot:
    def __init__(self, vector_db, llm_api, n_results=2):
        self.vector_db = vector_db
        self.llm_api = llm_api
        self.n_results = n_results

    def chat(self, user_query):
        # 1. Retrieval
        search_results = self.vector_db.search(user_query, self.n_results)

         # 2. Construct Prompt
        prompt = self.llm_api.build_prompt(
            prompt_template=prompt_template, context=search_results['documents'][0], query=user_query)

        print("===Reconstruct prompt with RAG===")
        print(prompt + "\n")

        # 3. Call LLM
        response = self.llm_api.get_completion(prompt)
        return response

def llmmager_init():
    """Initialize OpenAI operations object"""
    client = OpenAI()
    return LLMManager(client, "gpt-3.5-turbo-1106")


if __name__== "__main__":

    user_query = "how many parameters does llama 2 have?"
    index_name = "es_index_tmp_demo"

    llmmager = llmmager_init()

    # 0. Call LLM directly without RAG
    print(("===Prompt=== %s" % user_query))
    response = llmmager.get_completion(user_query)

    print("===Response without RAG===")
    print(response + "\n")

    collection_name = "llama2_docs"
    vector_db = MyVectorDBConnector(collection_name, llmmager.get_embeddings)

    # Create a RAG bot that internally calls the vector database, reconstructs the prompt
    bot = RAG_Bot(
        vector_db,
        llm_api=llmmager
    )

    user_query = "llama 2有多少参数?"

    response = bot.chat(user_query)

    print("===Response with RAG===")
    print(response)
