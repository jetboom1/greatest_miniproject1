import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
img = cv2.imread('data/1.jpg')

text = pytesseract.image_to_string(img, lang='ukr+eng')
with open('1.txt', 'w', encoding='utf-8') as file:
    file.write(text)