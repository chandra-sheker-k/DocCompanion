
import markdown
from bs4 import BeautifulSoup

def extract(path):
    with open(path, encoding="utf-8") as file:
        html = markdown.markdown(file.read())
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(), 1