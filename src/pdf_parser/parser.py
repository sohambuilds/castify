import PyPDF2

def parse_pdf(file_path):
    text = ""
    metadata = {}

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        metadata = reader.metadata
        for page in reader.pages:
            text += page.extract_text() + "\n"

    return text.strip(), metadata

def extract_title(metadata):
    return metadata.get('/Title', 'Untitled')

def extract_author(metadata):
    return metadata.get('/Author', 'Unknown')