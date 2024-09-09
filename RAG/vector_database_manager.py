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
        """向量数据库操作对象"""

        chroma_client = chromadb.HttpClient(host="localhost", port='8000')  # docker客户端模式

        # chroma_client = chromadb.Client(Settings(allow_reset=True)) #内存模式
        # # 为了演示，实际不需要每次 reset()
        # chroma_client.reset()

        # chroma_client = chromadb.Client(Settings(
        #     allow_reset=False,  # 确保不会每次启动时重置数据
        #     chroma_db_impl="sqlite",  # 使用 SQLite 作为数据库实现
        #     persist_directory="./data/chroma_data"  # 数据存储路径
        # ))

        # chroma_client = chromadb.PersistentClient(path="./data/chroma_data")  # 数据保存在磁盘 sqlite

        # Create or get a collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name
        )

        # 创建一个 collection
        self.collection = chroma_client.get_or_create_collection(
            name=collection_name)
        self.embedding_fn = embedding_fn

    def add_documents(self, documents, ids):
        '''向 collection 中添加文档与向量'''
        self.collection.add(
            embeddings=self.embedding_fn(documents),  # 每个文档的向量
            documents=documents,  # 文档的原文
            # ids=[f"id{i}" for i in range(len(documents))]  # 每个文档的 id
            ids=ids
        )

        # 如果 Chroma 收到一个文档列表，它会自动标记并使用集合的嵌入函数嵌入这些文档（如果在创建集合时没有提供嵌入函数，则使用默认值）。Chroma也会存储文档本身。如果文档过大，无法使用所选的嵌入函数嵌入，则会出现异常。
        # 每个文档必须有一个唯一的相关ID。尝试.添加相同的ID两次将导致错误。可以为每个文档提供一个可选的元数据字典列表，以存储附加信息并进行过滤。
        # 或者，您也可以直接提供文档相关嵌入的列表，Chroma将存储相关文档，而不会自行嵌入。
        # collection.add(
        #     embeddings=[[1.2, 2.3, 4.5], [6.7, 8.2, 9.2]],
        #     documents=["This is a document", "This is another document"],
        #     metadatas=[{"source": "my_source"}, {"source": "my_source"}],
        #     ids=["id1", "id2"]
        # )
        # 触发重新计算 ANN 索引（如果支持的话）
        # self._rebuild_index_if_needed()

    # def _rebuild_index_if_needed(self):
    #     # 根据需要手动触发重新计算索引
    #     # 这仅是示例，具体实现取决于所使用的库
    #     pass

    # def reset_collection(self):
    #     self.chroma_client.reset()  # 可能需要根据具体实现
    #     self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)

    def get_document_by_id(self, document_ids) -> tuple[list[str],list[str]]:
        # results = self.collection.get(ids=[document_id])
        results = self.collection.get(ids=document_ids)
        # return results["documents"][0] if results["documents"] else None
        return results["ids"], results["documents"]

    def search(self, query, top_n):
        '''检索向量数据库'''
        results = self.collection.query(
            query_embeddings=self.embedding_fn([query]),
            n_results=top_n
        )
        return results


if __name__=="__main__":

    client = OpenAI()

    llmmager = LLMManager(client, 'text-embedding-ada-002')

    collection_name = "llama2_docs"
    # collection_name = "demo"
    # Create a vector database object and add documents
    vector_db = MyVectorDBConnector(collection_name, llmmager.get_embeddings_default)

    ids, docs = load_docs()

    # 检查文档是否存在
    existing_document = vector_db.get_document_by_id(ids)
    # 没有生成向量的新文档
    new_ids = set(ids) - set(existing_document[0])

    # 原序保留需要生成向量的文档列表
    add_ids = []
    add_docs = []

    for id, doc in zip(ids, docs):
        if id in new_ids:
            add_ids.append(id)
            add_docs.append(doc)

    if len(add_ids) > 0:
        # # 文档不存在，添加新文档
        # # 加入一次就可以，向向量数据库中添加文档
        # # Extract text from the specified pages of the PDF
        # paragraphs = extract_text_from_pdf(
        #     "data/llama2.pdf",
        #     page_numbers=[3, 4],
        #     min_line_length=10
        # )
        # vector_db.add_documents(paragraphs)
        vector_db.add_documents(documents=add_docs, ids=add_ids)
        print("文档已添加" + "\n")
    else:
        print("文档已存在，无需重复添加" + "\n")

    user_query = "Llama 2有多少参数"
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

