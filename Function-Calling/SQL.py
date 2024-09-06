import json
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from Utils import print_json


_ = load_dotenv(find_dotenv())


client = OpenAI()


def get_sql_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=[{  # Extracted from OpenAI's official example https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb
            "type": "function",
            "function": {
                "name": "ask_database",
                "description": "Use this function to answer user questions about business. \
                            Output should be a fully formed SQL query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": f"""
                            SQL query extracting info to answer the user's question.
                            SQL should be written using this database schema:
                            {database_schema_string}
                            The query should be returned in plain text, not in JSON.
                            The query should only contain grammars supported by SQLite.
                            """,
                        }
                    },
                    "required": ["query"],
                }
            }
        }],
    )
    return response.choices[0].message

# Describe the database schema
database_schema_string = """
CREATE TABLE orders (
    id INT PRIMARY KEY NOT NULL, -- Primary key, cannot be null
    customer_id INT NOT NULL, -- Customer ID, cannot be null
    product_id STR NOT NULL, -- Product ID, cannot be null
    price DECIMAL(10,2) NOT NULL, -- Price, cannot be null
    status INT NOT NULL, -- Order status, integer type, cannot be null. 0 represents pending payment, 1 represents paid, 2 represents refunded
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time, default to the current time
    pay_time TIMESTAMP -- Payment time, can be null
);
"""


# Create a database connection
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Create the orders table
cursor.execute(database_schema_string)

# Insert 5 explicit mock records
mock_data = [
    (1, 1001, 'TSHIRT_1', 50.00, 0, '2023-09-12 10:00:00', None),
    (2, 1001, 'TSHIRT_2', 75.50, 1, '2023-09-16 11:00:00', '2023-08-16 12:00:00'),
    (3, 1002, 'SHOES_X2', 25.25, 2, '2023-10-17 12:30:00', '2023-08-17 13:00:00'),
    (4, 1003, 'SHOES_X2', 25.25, 1, '2023-10-17 12:30:00', '2023-08-17 13:00:00'),
    (5, 1003, 'HAT_Z112', 60.75, 1, '2023-10-20 14:00:00', '2023-08-20 15:00:00'),
    (6, 1002, 'WATCH_X001', 90.00, 0, '2023-10-28 16:00:00', None)
]

for record in mock_data:
    cursor.execute('''
    INSERT INTO orders (id, customer_id, product_id, price, status, create_time, pay_time)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', record)

# Commit the transaction
conn.commit()


def ask_database(query):
    cursor.execute(query)
    records = cursor.fetchall()
    return records


def single_table():
    # prompt = "October's sales"
    prompt = "Calculate monthly sales for each product"
    # prompt = "Which user has the highest spending? How much?"

    messages = [
        {"role": "system", "content": "You are a data analyst. Answer questions based on database data."},
        {"role": "user", "content": prompt}
    ]
    response = get_sql_completion(messages)
    if response.content is None:
        response.content = ""
    messages.append(response)
    print("====Function Calling====")
    print_json(response)

    if response.tool_calls is not None:
        tool_call = response.tool_calls[0]
        if tool_call.function.name == "ask_database":
            arguments = tool_call.function.arguments
            args = json.loads(arguments)
            print("====SQL====")
            print(args["query"])
            result = ask_database(args["query"])
            print("====DB Records====")
            print(result)

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "ask_database",
                "content": str(result)
            })
            response = get_sql_completion(messages)
            print("====Final Response====")
            print(response.content)


def multi_table():
    # Describe the database schema
    database_schema_string = """
    CREATE TABLE customers (
        id INT PRIMARY KEY NOT NULL, -- Primary key, cannot be null
        customer_name VARCHAR(255) NOT NULL, -- Customer name, cannot be null
        email VARCHAR(255) UNIQUE, -- Email, unique
        register_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Registration time, default to current time
    );
    CREATE TABLE products (
        id INT PRIMARY KEY NOT NULL, -- Primary key, cannot be null
        product_name VARCHAR(255) NOT NULL, -- Product name, cannot be null
        price DECIMAL(10,2) NOT NULL -- Price, cannot be null
    );
    CREATE TABLE orders (
        id INT PRIMARY KEY NOT NULL, -- Primary key, cannot be null
        customer_id INT NOT NULL, -- Customer ID, cannot be null
        product_id INT NOT NULL, -- Product ID, cannot be null
        price DECIMAL(10,2) NOT NULL, -- Price, cannot be null
        status INT NOT NULL, -- Order status, integer type, cannot be null. 0 represents pending payment, 1 represents paid, 2 represents refunded
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Creation time, default to current time
        pay_time TIMESTAMP -- Payment time, can be null
    );
    """

    # prompt = "Calculate monthly sales for each product"
    prompt = "Who is the highest spender this week? What products did they buy? How many of each product did they buy? How much did they spend?"
    messages = [
        {"role": "system", "content": "You are a data analyst. Answer user questions based on tables in the database."},
        {"role": "user", "content": prompt}
    ]
    response = get_sql_completion(messages)
    print(response.tool_calls[0].function.arguments)


if __name__ == '__main__':
    single_table()
    multi_table()

# The process tracking is as follows:
# test1: single_table(), prompt = "Calculate monthly sales for each product"
# test2: multi_table(), prompt = "Who is the highest spender this week? What products did they buy? How many of each product did they buy? How much did they spend?"

# ************************************************************************************************************************
#
# ====Function Calling====
# {
#     "content": "",
#     "role": "assistant",
#     "function_call": null,
#     "tool_calls": [
#         {
#             "id": "call_gWYpGG9AYtvIT18vvyXQelcv",
#             "function": {
#                 "arguments": "{\"query\":\"SELECT strftime('%Y-%m', create_time) AS month, product_id, SUM(price) AS total_sales FROM orders WHERE status = 1 GROUP BY month, product_id ORDER BY month, product_id;\"}",
#                 "name": "ask_database"
#             },
#             "type": "function"
#         }
#     ],
#     "refusal": null
# }
# ====SQL====
# SELECT strftime('%Y-%m', create_time) AS month, product_id, SUM(price) AS total_sales FROM orders WHERE status = 1 GROUP BY month, product_id ORDER BY month, product_id;
# ====DB Records====
# [('2023-09', 'TSHIRT_2', 75.5), ('2023-10', 'HAT_Z112', 60.75), ('2023-10', 'SHOES_X2', 25.25)]
# ====Final Response====
# The monthly sales for each product are as follows:
#
# - In September 2023, product TSHIRT_2 had total sales of $75.50.
# - In October 2023, product HAT_Z112 had total sales of $60.75 and product SHOES_X2 had total sales of $25.25.
# {"query":"SELECT customer_id, SUM(price) AS total_spent FROM orders WHERE strftime('%Y-%W', create_time) = strftime('%Y-%W', 'now') GROUP BY customer_id ORDER BY total_spent DESC LIMIT 1;"}
