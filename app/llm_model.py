import pdfplumber
from docx import Document
import concurrent.futures
import json
import requests

# Функции для извлечения текста
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

# Параллельная обработка файлов
def process_files_concurrently(file1, file2):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_pdf = executor.submit(extract_text_from_pdf, file1)
        future_docx = executor.submit(extract_text_from_docx, file2)
        document1 = future_pdf.result()
        document2 = future_docx.result()
    return document1, document2

# основная функция
def llm_def(question, id1, id2, temperature=0.0):
    headers = {"Content-Type": "application/json"}
    file1 = f"{id1}.pdf"
    file2 = f"{id2}.docx"
    document1, document2 = process_files_concurrently(file1, file2)
    body1 = {
            "model": "local-model",
            "messages": [{"role": "user", "content": f"{question}\n{document1}"}],
            "temperature": temperature
    }
    body2 = {
            "model": "local-model",
            "messages": [{"role": "user", "content": f"{question}\n{document2}"}],
            "temperature": temperature
    }
    # Преобразуем тело запроса в JSON-формат
    jsondata1 = json.dumps(body1, ensure_ascii=False).encode("utf8")
    jsondata2 = json.dumps(body2, ensure_ascii=False).encode("utf8")
    # Выполняем запросы к локальному серверу
    web1 = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, data=jsondata1, timeout=16000)
    web2 = requests.post("http://localhost:1234/v1/chat/completions", headers=headers, data=jsondata2, timeout=16000)
    # Обработка ответа от сервера
    result1 = web1.json()
    result2 = web2.json()
    # Извлекаем сообщения из ответа
    try:
        message1 = result1['choices'][0]['message']['content'].encode('utf-8').decode()
    except KeyError:
        message1 = result1.get('error', {}).get('message', 'Ошибка при обработке запроса')
    try:
        message2 = result2['choices'][0]['message']['content'].encode('utf-8').decode()
    except KeyError:
        message2 = result2.get('error', {}).get('message', 'Ошибка при обработке запроса')
    return message1.strip(), message2.strip()