import json


class NLU:
    def __init__(self, client, bussinessRequirement):
        self.client = client
        self.prompt_template = f"""
            {bussinessRequirement.instruction}\n\n{bussinessRequirement.output_format}\n\n{bussinessRequirement.examples}\n\nUser input:\n__INPUT__"""

    def _get_completion(self, prompt, model="gpt-3.5-turbo"):
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,  # Randomness of the model output, 0 means minimal randomness
            response_format={"type": "json_object"},
        )
        semantics = json.loads(response.choices[0].message.content)
        return {k: v for k, v in semantics.items() if v}

    def parse(self, user_input):
        prompt = self.prompt_template.replace("__INPUT__", user_input)
        return self._get_completion(prompt)
