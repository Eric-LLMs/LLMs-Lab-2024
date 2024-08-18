import copy

from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

from NLU import NLU
from DST import DST
from MockedDB import MockedDB
from BussinessRequirement import BussinessRequirement

_ = load_dotenv()

client = OpenAI()


class DialogManager:
    def __init__(self, prompt_templates):
        self.state = {}
        self.session = [
            {
                "role": "system",
                "content": "You are a customer service representative for mobile data plans, your name is Xiao Gua. You can help users choose the most suitable data plan."
            }
        ]
        self.nlu = NLU(client, BussinessRequirement())
        self.dst = DST()
        self.db = MockedDB()
        self.prompt_templates = prompt_templates

    def _wrap(self, user_input, records):
        if records:
            prompt = self.prompt_templates["recommand"].replace(
                "__INPUT__", user_input)
            r = records[0]
            for k, v in r.items():
                prompt = prompt.replace(f"__{k.upper()}__", str(v))
        else:
            prompt = self.prompt_templates["not_found"].replace(
                "__INPUT__", user_input)
            for k, v in self.state.items():
                if "operator" in v:
                    prompt = prompt.replace(
                        f"__{k.upper()}__", v["operator"] + str(v["value"]))
                else:
                    prompt = prompt.replace(f"__{k.upper()}__", str(v))
        return prompt

    def _call_chatgpt(self, prompt, model="gpt-3.5-turbo"):
        session = copy.deepcopy(self.session)
        session.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=model,
            messages=session,
            temperature=0,
        )
        return response.choices[0].message.content

    def run(self, user_input):
        # Call NLU to get semantic parsing
        semantics = self.nlu.parse(user_input)
        print("===semantics===")
        print(semantics)

        # Call DST to update multi-turn state
        self.state = self.dst.update(self.state, semantics)
        print("===state===")
        print(self.state)

        # Retrieve from DB based on the state, get candidates that meet the conditions
        records = self.db.retrieve(**self.state)

        # Assemble prompt to call chatgpt
        prompt_for_chatgpt = self._wrap(user_input, records)
        print("===gpt-prompt===")
        print(prompt_for_chatgpt)

        # Call chatgpt to get a reply
        response = self._call_chatgpt(prompt_for_chatgpt)

        # Maintain the current user input and system response in the chatgpt session
        self.session.append({"role": "user", "content": user_input})
        self.session.append({"role": "assistant", "content": response})
        return response

