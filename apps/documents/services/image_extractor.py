
from PIL import Image
import pytesseract

def extract(path):

    image = Image.open(path)
    text = pytesseract.image_to_string(image)

    return {
        "text": text,
        "pages": [
            {
                "page": 1,
                "text": text,
            }
        ],
        "metadata": {
            "pages": 1
        },
    }