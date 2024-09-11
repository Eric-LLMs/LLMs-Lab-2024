# LLMs-Lab-2024

This repository contains projects, research, and educational resources focused on Large Language Models (LLMs).

## 1. Task-oriented Dialogue System

   This demo implements a multi-turn, task-oriented intelligent customer service system using the OpenAI API.
   
## 2. Function-Calling

This folder contains various demos showcasing the capabilities of Function Calling.

### Function Calling Demos

   - **`POI`**:
       
     This demo uses Amap's (Gaode Map) public API to retrieve information about hotels, restaurants, attractions, and other points of interest (POIs) near a specific location. It allows querying nearby POIs relative to a given point.

   - **`SQL`**:
       
     This demo demonstrates how Function Calling handles sophisticated database tasks and generates SQL queries.

   - **`Stream`**:
       
     This demo showcases examples of Function Calling in Stream mode.


## 3. RAG

This folder contains tree different **RAG (Retrieval-Augmented Generation)** pipelines. The first one is based on Elasticsearch (ES), the second one is based on a vector database, ChromaDB, and the last RAG Pipline show how to use data from tables in PDFs to perform RAG retrieval.
  

### Pipelines

- **`run_RAG_vector_database_pipeline`**:
    
  RAG Pipeline based on ChromaDB Vector Database.

      The Offline Steps are as follows:  

      | Document Loading      | Document Splitting  | Vectorization | Insert into Vector Database  |
      |-----------------------|---------------------|---------------|------------------------------|
      |          →            |        →            |      →        |               →              |
      
      The Online Steps are as follows:  
      
      | Receive User Query    | Vectorize User Query | Retrieve from Vector Database | Populate Prompt Template  | Call LLM with Final Prompt | Generate Response   |
      |-----------------------|----------------------|-------------------------------|---------------------------|----------------------------|---------------------|
      |           →           |           →          |                →              |                 →         |                →           |          →          |  


- **`run_RAG_ES_pipeline`**:
    
  RAG Pipeline based on Elasticsearch (ES).

- **`RAG_pipeline_pdf_table_processing`**:  
    
  In this RAG Pipline, use data from tables in PDFs to perform RAG retrieval.  
  
  Offline:  
    
  Convert PDF to images and extract tables from the images → Use GPT-4 to generate textual descriptions of the table images → Store the textual descriptions (documents), their embeddings (embeddings), and image URLs (metadatas) into the vector database.
    
  Online:
    
  Receive a query and search the vector database → Retrieve table image URLs from search results (based on similarity between textual descriptions and the query) → Use GPT-4 to query and retrieve information from the table images.
    
      
  The pipeline flowchart is as follows:
    
  ![Alt text](RAG/data/table_rag.png)

