import os
import sys
from selenium import webdriver
import requests
import PyPDF2

FIREFOX_DRIVER_PATH = '%s/geckodriver' % os.path.dirname(os.path.realpath(__file__))

INPUT_PATH = 'input/'
INPUT_FILENAME = 'lottery_results.pdf'
URL = 'https://dcra.dc.gov/mrv'

def download_pdf(pdf_url):
    file = '%s%s' % (INPUT_PATH, INPUT_FILENAME)
    response = requests.get(pdf_url, stream=True)

    with open(file,"wb+") as pdf:
        for chunk in response.iter_content(chunk_size=1024):
             if chunk:
                 pdf.write(chunk)

    return file


def get_pdf_url():

    driver = webdriver.Firefox(
        executable_path=FIREFOX_DRIVER_PATH,
    )

    driver.get(URL)
    elem = driver.find_element_by_css_selector('#block-system-main .field-items .field-item a')
    href = elem.get_attribute('href')
    driver.close()

    return href

def read_pdf(file):

    pdf_file = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    num_pages = pdf_reader.numPages

    i = 0
    while i < num_pages:
        page = pdf_reader.getPage(i)
        text = page.extractText()
        lines = text.splitlines()
        print lines
        i = i+1

    pdf_file.close()


def run():

    url = get_pdf_url()
    file = download_pdf(url)

    read_pdf(file)

run()

print 'finis'


