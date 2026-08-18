
from PIL import Image
import pytesseract
import io

def extract_image_text(pixmap) -> str:
    """
    Extract text from a PyMuPDF Pixmap using OCR.
    """
    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    return pytesseract.image_to_string(image)