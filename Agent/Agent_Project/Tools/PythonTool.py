import re
from langchain.tools import StructuredTool
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate

from Utils.CallbackHandlers import ColoredPrintHandler
from Utils.PrintUtils import CODE_COLOR
from langchain_openai import ChatOpenAI
from .ExcelTool import get_first_n_rows, get_column_names
from langchain_experimental.utilities import PythonREPL


class PythonCodeParser(BaseOutputParser):
    """Extract Python code from text returned by OpenAI."""

    @staticmethod
    def __remove_marked_lines(input_str: str) -> str:
        lines = input_str.strip().split('\n')
        if lines and lines[0].strip().startswith('```'):
            del lines[0]
        if lines and lines[-1].strip().startswith('```'):
            del lines[-1]

        ans = '\n'.join(lines)
        return ans

    def parse(self, text: str) -> str:
        # Use regex to find all Python code blocks
        python_code_blocks = re.findall(r'```python\n(.*?)\n```', text, re.DOTALL)
        # Extract Python code text from regex results
        python_code = None
        if len(python_code_blocks) > 0:
            python_code = python_code_blocks[0]
            python_code = self.__remove_marked_lines(python_code)
        return python_code


class ExcelAnalyser:
    """
    Analyze the content of a structured file (e.g., an Excel file) using a script.
    The input must include the full path of the file and specific analysis methods, criteria, threshold constants, etc.
    """

    def __init__(self, prompt_file="./prompts/tools/excel_analyser.txt", verbose=False):
        self.prompt = PromptTemplate.from_file(prompt_file)
        self.verbose = verbose
        self.verbose_handler = ColoredPrintHandler(CODE_COLOR)

    def analyse(self, query, filename):

        """Analyze the content of a structured file (e.g., an Excel file)."""

        # columns = get_column_names(filename)
        inspections = get_first_n_rows(filename, 3)

        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            model_kwargs={
                "seed": 42
            },
        )

        code_parser = PythonCodeParser()
        chain = self.prompt | llm | StrOutputParser()

        response = ""

        for c in chain.stream({
            "query": query,
            "filename": filename,
            "inspections": inspections
        }, config={
            "callbacks": [
                self.verbose_handler
            ] if self.verbose else []
        }):
            response += c

        code = code_parser.parse(response)

        if code:
            ans = query + "\n" + PythonREPL().run(code)
            return ans
        else:
            return "No executable Python code found."

    def as_tool(self):
        return StructuredTool.from_function(
            func=self.analyse,
            name="AnalyseExcel",
            description=self.__class__.__doc__.replace("\n", ""),
        )


if __name__ == "__main__":
    print(ExcelAnalyser().analyse(
        query="August sales",
        filename="../data/2023 August-September Sales Records.xlsx"
    ))
