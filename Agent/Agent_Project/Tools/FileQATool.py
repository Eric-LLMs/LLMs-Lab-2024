from typing import List
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.word_document import UnstructuredWordDocumentLoader
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI


class FileLoadFactory:
    @staticmethod
    def get_loader(filename: str):
        ext = get_file_extension(filename)
        if ext == "pdf":
            return PyPDFLoader(filename)
        elif ext == "docx" or ext == "doc":
            return UnstructuredWordDocumentLoader(filename)
        else:
            raise NotImplementedError(f"File extension {ext} not supported.")


def get_file_extension(filename: str) -> str:
    return filename.split(".")[-1]


def load_docs(filename: str) -> List[Document]:
    file_loader = FileLoadFactory.get_loader(filename)
    pages = file_loader.load_and_split()
    return pages


def ask_document(
        filename: str,
        query: str,
) -> str:
    """Answer a question based on the content of a PDF document."""

    raw_docs = load_docs(filename)
    if len(raw_docs) == 0:
        return "Sorry, the document content is empty."
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    documents = text_splitter.split_documents(raw_docs)
    if documents is None or len(documents) == 0:
        return "Unable to read document content."
    db = Chroma.from_documents(documents, OpenAIEmbeddings(model="text-embedding-ada-002"))
    qa_chain = RetrievalQA.from_chain_type(
        llm=OpenAI(
            temperature=0,
            model_kwargs={
                "seed": 42
            },
        ),  # Language model
        chain_type="stuff",  # Prompt organization method, explained later
        retriever=db.as_retriever()  # Retriever
    )
    # response = qa_chain.run(query + "(Please respond in Chinese)")
    response = qa_chain.run(query + "(Please respond in English)")
    return response


if __name__ == "__main__":
    filename = "../data/2023 October Sales Plan.docx"
    query = "What is the standard for achieving sales targets?"
    response = ask_document(filename, query)
    print(response)