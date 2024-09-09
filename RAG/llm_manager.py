class LLMManager:
    def __init__(self, client, model="gpt-3.5-turbo-1106"):
        self.client = client
        self.model = model

    def get_completion(self, prompt):
        '''Wrapper for the OpenAI API'''
        messages = [{"role": "user", "content": prompt}]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0,  # Controls the randomness of the model output, 0 means minimal randomness
        )
        return response.choices[0].message.content

    def build_prompt(self, prompt_template, **kwargs):
        '''Assign values to the prompt template'''
        inputs = {}
        for k, v in kwargs.items():
            if isinstance(v, list) and all(isinstance(elem, str) for elem in v):
                val = '\n\n'.join(v)
            else:
                val = v
            inputs[k] = val
        return prompt_template.format(**inputs)

    def get_embeddings(self, texts, model="text-embedding-ada-002"):
        '''set model="text-embedding-ada-002",Encapsulate the OpenAI Embedding model interface'''
        data = self.client.embeddings.create(input=texts, model=model).data
        return [x.embedding for x in data]

    def get_embeddings_default(self, texts):
        '''model=self.model,Encapsulate the OpenAI Embedding model interface'''
        data = self.client.embeddings.create(input=texts, model=self.model).data
        return [x.embedding for x in data]
