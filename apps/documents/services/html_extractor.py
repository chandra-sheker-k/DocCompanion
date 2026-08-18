
from bs4 import BeautifulSoup

def extract(path):
    with open(path, encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    return soup.get_text(), 1