from dotenv import load_dotenv, find_dotenv
from openai import OpenAI

from llm_manager import LLMManager
from vector_database_manager import MyVectorDBConnector
from RAG_Bot import RAG_Bot

# Load the local .env file which defines OPENAI_API_KEY
_ = load_dotenv(find_dotenv())


def llmmager_init():
    """Initialize OpenAI operations object"""
    client = OpenAI()
    return LLMManager(client, "gpt-3.5-turbo-1106")


if __name__ == "__main__":

    user_query = "how many parameters does llama 2 have?"
    index_name = "es_index_tmp_demo"

    llmmager = llmmager_init()

    # 0. Call LLM directly without RAG
    print("===Prompt===")
    print(user_query + '\n')

    response = llmmager.get_completion(user_query)

    print("===Response without RAG===")
    print(response + "\n")

    collection_name = "llama2_docs"
    vector_db = MyVectorDBConnector(collection_name, llmmager.get_embeddings)  # 向量数据库

    # 1. 创建一个RAG机器人，内部调用vector database , 封装了 RAG过程
    bot = RAG_Bot(
        vector_db,
        llm_api=llmmager
    )

    user_query = "llama 2有多少参数?"

    response = bot.chat(user_query)

    print("===Response with RAG===")
    print(response)

# The process tracking is as follows:
# ***************************************************************************************************************

# ==Prompt===
# how many parameters does llama 2 have?
#
# ===Response without RAG===
# Llama 2 has 3 parameters.
#
# ===Reconstruct prompt with RAG===
#
# You are a question-answering bot.
# Your task is to answer user questions based on the given known information below.
#
# Known Information:
# In this work, we develop and release Llama 2, a family of pretrained and fine-tuned LLMs, Llama 2 and Llama 2-Chat,
# at scales up to 70B parameters. On the series of helpfulness and safety benchmarks we tested, Llama 2-Chat models
# generally perform better than existing open-source models. They also appear to be on par with some of the
# closed-source models, at least on the human evaluations we performed (see Figures 1 and 3).
#
# In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs)
# ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned LLMs, called Llama 2-Chat, are optimized for
# dialogue use cases. Our models outperform open-source chat models on most benchmarks we tested, and based on our
# human evaluations for helpfulness and safety, may be a suitable substitute for closedsource models.
#
# User Question:
# llama 2有多少参数?
#
# If the known information does not contain the answer to the user's question, or if the known information is
# insufficient to answer the user's question, please respond directly with "I cannot answer your question."
# Please do not output information or answers that are not included in the known information.
# Please answer the user's question in both English and Chinese.
#
#
# ===Response with RAG===
# English: Llama 2 has parameters ranging in scale from 7 billion to 70 billion.
#
# Chinese: Llama 2的参数范围从70亿到700亿。
