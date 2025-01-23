import requests
import json
import os
from app.llm_model import llm_def


def pars_zakupki(pid):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(f"https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId={pid}", headers=headers)
        data = json.loads(response.text)
        files = data.get('files', [])
        name = data["name"]
        isElectronicContractExecutionRequired = data["isElectronicContractExecutionRequired"]# Условия исполнения контракта
        isContractGuaranteeRequired = data["isContractGuaranteeRequired"] # Обеспечение исполнения контракта
        licenseFiles = data["licenseFiles"] # Наличие сертификатов/лицензий // "licenseFiles": [],
        customer_name = data["customer"]["name"] # Заказчик
        federalLawName = data["federalLawName"] # Заключение происходит в соответствии с законом
        startDate = data["startDate"] # начало Даты проведения # график поставки?
        endDate = data["endDate"] # конец Даты проведения # график поставки?
        startCost = data["startCost"] # начальная стоимость
        nextCost = data["nextCost"] # следующая стоимость
        if files[0].get('name').endswith(".docx"):
            name_docx = files[0].get('name') # название файла docx
            doc_docx = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={files[0].get('id')}"# Документы docx
            name_pdf = files[1].get('name') # название файла pdf
            doc_pdf = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={files[1].get('id')}"# Документы pdf
        else:
            name_pdf = files[0].get('name') # название файла pdf
            doc_pdf = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={files[0].get('id')}"# Документы pdf
            name_docx = files[1].get('name') # название файла docx
            doc_docx = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={files[1].get('id')}"# Документы docx
        return name,isElectronicContractExecutionRequired,isContractGuaranteeRequired,licenseFiles,customer_name,federalLawName,startDate,endDate,startCost,nextCost,name_docx,doc_docx,name_pdf,doc_pdf
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    
def pars_files(pid):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(f"https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId={pid}", headers=headers)
        data = json.loads(response.text)
        files = data.get('files', [])
        if files[0].get('name').endswith(".docx"):
            file_id0 = files[0].get('id')
            file_id1 = files[1].get('id')
        else:
            file_id1 = files[0].get('id')
            file_id0 = files[1].get('id')
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    # удаление файлов если они есть перед скачиванием
    if os.path.exists(f"{file_id0}.docx"):
        try:
            os.remove(f"{file_id0}.docx")
            print(f"Файл {file_id0}.docx был успешно удалён.")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
    else:
        print(f"Файл {file_id0}.docx не существует.")
    
    if os.path.exists(f"{file_id1}.pdf"):
        try:
            os.remove(f"{file_id1}.pdf")
            print(f"Файл {file_id1}.pdf был успешно удалён.")
        except Exception as e:
            print(f"Ошибка при удалении файла: {e}")
    else:
        print(f"Файл {file_id1}.pdf не существует.")

    try:
        response = requests.get(f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file_id0}", stream=True)
        if response.status_code == 200:
            with open(f"{file_id0}.docx", 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024): # читаем по частям чтобы избежать переполнения памяти
                    file.write(chunk)
            print(f"Файл успешно скачан: {f"{file_id0}.docx"}")
        else:
            print(f"Ошибка при скачивании файла. Статус код: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    try:
        response = requests.get(f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file_id1}", stream=True)
        if response.status_code == 200:
            with open(f"{file_id1}.pdf", 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024): # читаем по частям чтобы избежать переполнения памяти
                    file.write(chunk)
            print(f"Файл успешно скачан: {f"{file_id1}.pdf"}")
        else:
            print(f"Ошибка при скачивании файла. Статус код: {response.status_code}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

def proverka_ks(url,p1,p2,p3,p4,p5,p6):
    name,isElectronicContractExecutionRequired,isContractGuaranteeRequired,licenseFiles,customer_name,federalLawName,startDate,endDate,startCost,nextCost,name_docx,doc_docx,name_pdf,doc_pdf = pars_zakupki(url)
    pars_files(url)
    prompt1 = f"Наименование закупки: {name}, "
    prompt2 = f"Обеспечение исполнения контракта указано: {isContractGuaranteeRequired}, "
    prompt3 = f"Наличие сертификатов/лицензий: {licenseFiles}, "
    prompt4 = f"График и этап поставки: {startDate} по {endDate}, "
    prompt5 = f"Максимальное значение цены контракта: {startCost} руб."
    prompt = ""
    if(p1 == True):
        prompt = prompt+prompt1
    if(p2 == True):
        prompt = prompt+prompt2
    if(p3 == True):
        if len(licenseFiles) != 0:
            prompt = prompt+prompt3
    if(p4 == True):
        prompt = prompt+prompt4
    if(p5 == True):
        prompt = prompt+prompt5
    final_prompt = f'''
    Вам будет предоставлен текст. Ваша задача — определить, соответствует данный текст нужным характеристикам или нет
    Характеристики: {prompt}
    Пожалуйста, проанализируйте текст и ответьте только одним словом:
    - `true` — если текст соответствует всем характеристикам.
    - `false` — если текст не соответствует всем характеристикам.
    Вот текст:
    '''
    doc_pdf = doc_pdf.replace("https://zakupki.mos.ru/newapi/api/FileStorage/Download?id=", "")
    doc_docx = doc_docx.replace("https://zakupki.mos.ru/newapi/api/FileStorage/Download?id=", "")
    perem1,perem2 = llm_def(final_prompt,doc_pdf,doc_docx)
    if (perem1 == 'true' or perem2 == 'true'):
        print("True")
        return True
    else: 
        print("False")
        return False