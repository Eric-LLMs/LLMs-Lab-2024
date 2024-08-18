class BussinessRequirement:
    def __init__(self, ):
        self.instruction = """
        Your task is to identify the conditions that users have when choosing mobile data plans.
        Each data plan product has three attributes: name, monthly fee (price), and monthly data.
        Based on the user input, identify the user's requirements for these three attributes.
        """

        # Output format
        self.output_format = """
        Output in JSON format.
        1. The value of the name field should be a string, and it must be one of the following: Economy Plan, Travel Plan, Unlimited Plan, Campus Plan, or null;
    
        2. The value of the price field should be a structure or null, containing two fields:
        (1) operator, a string, with possible values: '<=' (less than or equal to), '>=' (greater than or equal to), '==' (equal to)
        (2) value, an integer
    
        3. The value of the data field should be a structure or null, containing two fields:
        (1) operator, a string, with possible values: '<=' (less than or equal to), '>=' (greater than or equal to), '==' (equal to)
        (2) value, an integer or string, where the string type can only be 'unlimited'
    
        4. The user's intent may include sorting by price or data, indicated by the sort field, which should be a structure:
        (1) In the structure, "ordering"="descend" indicates sorting in descending order, with the "value" field storing the field to be sorted.
        (2) In the structure, "ordering"="ascend" indicates sorting in ascending order, with the "value" field storing the field to be sorted.
    
        Only output fields mentioned by the user, do not infer any fields not directly mentioned by the user.
        DO NOT OUTPUT NULL-VALUED FIELD! Ensure the output can be loaded by json.loads.
        """

        self.examples = """
        Cheap plan: {"sort":{"ordering"="ascend","value"="price"}}
        Is there an unlimited data plan: {"data":{"operator":"==","value":"unlimited"}}
        Plan with the most data: {"sort":{"ordering"="descend","value"="data"}}
        Which plan with more than 100GB of data is the cheapest: {"sort":{"ordering"="ascend","value"="price"},"data":{"operator":">=","value":100}}
        Plan with a monthly fee of no more than 200: {"price":{"operator":"<=","value":200}}
        I want the plan with a monthly fee of 180: {"price":{"operator":"==","value":180}}
        Economy Plan: {"name":"Economy Plan"}
        Luxury Plan: {"name":"Unlimited Plan"}
        """

        self.prompt_templates = {
            "recommand": "User said: __INPUT__ \n\nIntroduce the following product to the user: __NAME__, monthly fee of __PRICE__ yuan, with __DATA__ GB of data per month.",
            "not_found": "User said: __INPUT__ \n\nNo product found that meets the criteria of __PRICE__ yuan price and __DATA__ GB of data. Ask the user if they have any other preferences."
        }
