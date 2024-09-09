import os
from typing import List

from elasticsearch7 import Elasticsearch, helpers
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from dotenv import load_dotenv
import nltk
import re

import warnings
warnings.simplefilter("ignore")  # Ignore some warnings from Elasticsearch

from utils import extract_text_from_pdf, prompt_template

# When using nltk, install the version with pip install nltk==3.8.1.
# Versions above this might not find punkt_tap in nltk_data and could raise an exception.
# nltk.download('punkt')  # For tokenization, stemming, sentence splitting, etc.
# nltk.download('stopwords')  # For English stopword corpus

_ = load_dotenv()


class ElasticsearchOperations:
    def __init__(self, base_url, username, password):
        """
        :param base_url: base_url
        :param username: username
        :param password: password
        :return: ElasticsearchOperations object
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        # Tip: To run locally, print(ELASTICSEARCH_BASE_URL) below to get the real configuration

        # 1. Create an Elasticsearch connection
        # es = Elasticsearch(
        #     hosts=[self.base_url],  # Service address and port
        #     http_auth=(self.username, self.password),  # Username, password
        # )

        # Create Elasticsearch connection
        try:
            self.es = Elasticsearch(
                hosts=[self.base_url],  # Service address and port
                http_auth=(self.username, self.password)  # Username, password
            )
            # Test the connection
            if not self.es.ping():
                print("Cannot connect to Elasticsearch")
        except Exception as e:
            print(f"Error connecting to Elasticsearch: {e}")

    def to_keywords(self, input_string):
        '''Keep only keywords from the (English) text'''
        # Replace all non-alphanumeric characters with spaces using regex
        no_symbols = re.sub(r'[^a-zA-Z0-9\s]', ' ', input_string)
        word_tokens = word_tokenize(no_symbols)
        # Load stopwords
        stop_words = set(stopwords.words('english'))
        ps = PorterStemmer()
        # Remove stopwords and get word stems
        filtered_sentence = [ps.stem(w)
                             for w in word_tokens if not w.lower() in stop_words]
        return ' '.join(filtered_sentence)

    def input_data_es(self, paragraphs, index_name):
        """
        Import text corpus, data is a collection of paragraphs with multiple sentences
        :param paragraphs: Collection of paragraphs with multiple sentences
        :param index_name: Index name
        :return: null
        """
        # 2. Define the index name
        index_name = index_name

        # 3. If the index exists, delete it (for demonstration purposes, not needed in real applications)
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)

        # 4. Create the index
        self.es.indices.create(index=index_name)

        # 5. Bulk data insertion command
        actions = [
            {
                "_index": index_name,
                "_source": {
                    "keywords": self.to_keywords(para),
                    "text": para
                }
            }
            for para in paragraphs
        ]

        # 6. Insert text data
        helpers.bulk(self.es, actions)

    def search(self, index_name: str, query_string: str, top_n: int = 3) -> List[str]:
        # Elasticsearch query
        search_query = {
            "match": {
                "keywords": self.to_keywords(query_string)
            }
        }
        res = self.es.search(index=index_name, query=search_query, size=top_n)
        return [hit["_source"]["text"] for hit in res["hits"]["hits"]]


if __name__ == "__main__":
    # Load configuration files
    ELASTICSEARCH_BASE_URL = os.getenv('ELASTICSEARCH_BASE_URL')
    ELASTICSEARCH_NAME = os.getenv('ELASTICSEARCH_NAME')
    ELASTICSEARCH_PASSWORD = os.getenv('ELASTICSEARCH_PASSWORD')
    index_name = "es_index_tmp_demo"

    # Extract text data from PDF, handle when importing data to ES for the first time
    paragraphs = extract_text_from_pdf("data/llama2.pdf", min_line_length=10)
    # for para in paragraphs[:4]:
    #     print(para + "\n")

    ES = ElasticsearchOperations(ELASTICSEARCH_BASE_URL, ELASTICSEARCH_NAME, ELASTICSEARCH_PASSWORD)

    # Import text data into ES
    ES.input_data_es(paragraphs, index_name)

    query_string = "how many parameters does llama 2 have?"
    results = ES.search(index_name, query_string, 2)
    for r in results:
        print(r + "\n")

