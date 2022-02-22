
import pytesseract
import cv2
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
hodoriv = [cv2.imread('data/hodoriv/{}.jpg'.format(i)) for i in range(1, 6)]
zbarazh = [cv2.imread('data/zbarazh/{}.jpg'.format(i)) for i in range(1, 8)]
strymilo_kamenets = [cv2.imread('data/strymilo-kamenets/{}.jpg'.format(i)) for i in range(1, 6)]

text = ''
for img in hodoriv:
    text += pytesseract.image_to_string(img, lang='ukr+eng')
    text += '\n'
text = text.replace('ті?', 'm2')
text = text.replace('тп?', 'm2')
text = text.replace('m?', 'm2')
with open('text/hodoriv.txt', 'w', encoding='utf-8') as file:
    file.write(text)
text = ''
for img in zbarazh:
    text += pytesseract.image_to_string(img, lang='ukr+eng')
    text += '\n'
with open('text/zbarazh.txt', 'w', encoding='utf-8') as file:
    file.write(text)
text = ''
for img in strymilo_kamenets:
    text += pytesseract.image_to_string(img, lang='ukr+eng')
    text += '\n'
with open('text/stymilo-kamenets.txt', 'w', encoding='utf-8') as file:
    file.write(text)