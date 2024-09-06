import json


def print_json(data):
    """
    Print the parameter. If the parameter is structured (such as a dictionary or list), it is printed in formatted JSON;
    otherwise, the value is printed directly.
    """
    if hasattr(data, 'model_dump_json'):
        data = json.loads(data.model_dump_json())

    if isinstance(data, list):
        for item in data:
            print_json(item)
    elif isinstance(data, dict):
        print(json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ))
    else:
        print(data)
