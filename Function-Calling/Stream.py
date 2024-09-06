from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from Utils import print_json

_ = load_dotenv(find_dotenv())

client = OpenAI()


def get_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
        tools=[{
            "type": "function",
            "function": {
                "name": "sum",
                "description": "Calculate the sum of a set of numbers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "numbers": {
                            "type": "array",
                            "items": {
                                "type": "number"
                            }
                        }
                    }
                }
            }
        }],
        stream=True,    # Enable streaming output
    )
    return response


prompt = "1+2+3"
# prompt = "Who are you"

messages = [
    {"role": "system", "content": "You are a primary school math teacher, and you need to teach students addition"},
    {"role": "user", "content": prompt}
]

response = get_completion(messages)

function_name, args, text = "", "", ""

print("====Streaming====")

# The tokens from the stream need to be concatenated to get the full call
for msg in response:
    delta = msg.choices[0].delta
    if delta.tool_calls:
        if not function_name:
            function_name = delta.tool_calls[0].function.name
            print(function_name)
        args_delta = delta.tool_calls[0].function.arguments
        print(args_delta)  # Print the data received each time
        args = args + args_delta
    elif delta.content:
        text_delta = delta.content
        print(text_delta)
        text = text + text_delta

print("====done!====")

if function_name or args:
    print(function_name)
    print_json(args)
if text:
    print(text)

# The process tracking is as follows:

# ************************************************************************************************************************
# ====Streaming====
# sum
#
# {"
# numbers
# ":[
# 1
# ,
# 2
# ,
# 3
# ]}
# ====done!====
# sum
# {"numbers":[1,2,3]}
