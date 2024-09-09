from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


def extract_text_from_pdf(filename, page_numbers=None, min_line_length=1):
    '''Extract text from a PDF file (by specified page numbers)'''
    paragraphs = []
    buffer = ''
    full_text = ''
    # Extract the entire text
    for i, page_layout in enumerate(extract_pages(filename)):
        # If a page range is specified, skip pages outside the range
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text() + '\n'
    # Separate text into paragraphs by blank lines
    lines = full_text.split('\n')
    for text in lines:
        if len(text) >= min_line_length:
            buffer += (' ' + text) if not text.endswith('-') else text.strip('-')
        elif buffer:
            paragraphs.append(buffer)
            buffer = ''
    if buffer:
        paragraphs.append(buffer)
    return paragraphs


def load_docs(path:str = './data/docs') -> tuple[list[str],list[str]]:
    docs = []
    ids = []
    with open(path, 'r') as file:
        for line in file:
            id, doc = line.strip().split('#')
            ids.append(id)
            docs.append(doc)
    return ids, docs


prompt_template = """
        You are a question-answering bot.
        Your task is to answer user questions based on the given known information below.

        Known Information:
        {context}

        User Question:
        {query}

        If the known information does not contain the answer to the user's question, or if the known information is insufficient to answer the user's question, please respond directly with "I cannot answer your question."
        Please do not output information or answers that are not included in the known information.
        Please answer the user's question in both English and Chinese.
        """


if __name__ == "__main__":
    paragraphs = extract_text_from_pdf("data/llama2.pdf", min_line_length=10)
    for para in paragraphs[:4]:
        print(para + "\n")
