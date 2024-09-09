import os
# Load environment variables
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from elasticsearch_operations import ElasticsearchOperations
from llm_manager import LLMManager

from utils import prompt_template

_ = load_dotenv(find_dotenv())  # Load the local .env file which defines OPENAI_API_KEY


def es_init():
    """Initialize Elasticsearch operations object"""
    # Load configuration files
    ELASTICSEARCH_BASE_URL = os.getenv('ELASTICSEARCH_BASE_URL')
    ELASTICSEARCH_NAME = os.getenv('ELASTICSEARCH_NAME')
    ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')

    return ElasticsearchOperations(ELASTICSEARCH_BASE_URL, ELASTICSEARCH_NAME, ELASTICSEARCH_PASSWORD)


def llmmager_init():
    """Initialize OpenAI operations object"""
    client = OpenAI()
    return LLMManager(client, "gpt-3.5-turbo-1106")


if __name__ == "__main__":
    user_query = "how many parameters does llama 2 have?"
    index_name = "es_index_tmp_demo"

    ES = es_init()
    client = llmmager_init()

    # 0. Call LLM directly without RAG
    print(("===Prompt=== %s" % user_query))
    response = client.get_completion(user_query)

    print("===Response without RAG===")
    print(response)

    print("===Reconstruct prompt with RAG===")
    # 1. Search
    search_results = ES.search(index_name, user_query, 2)

    # 2. Build the Prompt
    prompt = client.build_prompt(prompt_template, context=search_results, query=user_query)
    print("===Prompt===")
    print(prompt)

    # 3. Call LLM with RAG
    response = client.get_completion(prompt)

    print("===Response with RAG===")
    print(response)


# *********************************************************************************
#
#  The process tracking is as follows:
#
# *********************************************************************************


# ===Prompt=== how many parameters does llama 2 have?
# ===Response without RAG===
# Llama 2 has 3 parameters.
# ===Reconstruct prompt with RAG===
# ===Prompt===
#
# You are a question-answering bot.
# Your task is to answer user questions based on the given known information below.
#
# Known Information:
# Llama 2 comes in a range of parameter sizes—7B, 13B, and 70B—as well as pretrained and fine-tuned variations.
#
# 1. Llama 2, an updated version of Llama 1, trained on a new mix of publicly available data. We also increased the size
# of the pretraining corpus by 40%, doubled the context length of the model, and adopted grouped-query attention
# (Ainslie et al., 2023). We are releasing variants of Llama 2 with 7B, 13B, and 70B parameters.
# We have also trained 34B variants, which we report on in this paper but are not releasing.§
#
# User Question:
# how many parameters does llama 2 have?
#
# If the known information does not contain the answer to the user's question, or if the known information is
# insufficient to answer the user's question, please respond directly with "I cannot answer your question."
# Please do not output information or answers that are not included in the known information.
# Please answer the user's question in both English and Chinese.
#
# ===Response with RAG===
# English: Llama 2 comes in a range of parameter sizes—7B, 13B, and 70B.
#
# Chinese: Llama 2有一系列的参数大小—7B、13B和70B。
