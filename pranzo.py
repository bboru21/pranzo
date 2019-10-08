import os
import sys
from selenium import webdriver
import requests
import PyPDF2
import pandas as pd

FIREFOX_DRIVER_PATH = '%s/geckodriver' % os.path.dirname(os.path.realpath(__file__))

INPUT_PATH = 'input/'
INPUT_FILENAME = 'lottery_results.pdf'
URL = 'https://dcra.dc.gov/mrv'
DESIRED_LOCATION = 'Georgetown'

OUTPUT_PATH = 'output/'
OUTPUT_FILENAME = 'lottery_results.xlsx'

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

def divide_chunks(l, n):

    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def filter_by_location(current_list):

    new_list = []

    if DESIRED_LOCATION:
        for item in current_list:
            if DESIRED_LOCATION in item:
                new_list.append(item)
        return new_list
    else:
        return current_List

def read_pdf(file):

    pdf_file = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    num_pages = pdf_reader.numPages

    i = 0
    data = []
    while i < num_pages:
        page = pdf_reader.getPage(i)
        text = page.extractText()
        lines = text.splitlines()

        lines = lines[8:] # remove month and columns
        lines = list(divide_chunks(lines, 7))
        lines = filter_by_location(lines)
        data = data + lines

        i = i+1

    df = pd.DataFrame(data, columns =['Site Permit', 'Business Name', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    with pd.ExcelWriter('%s%s' % (OUTPUT_PATH, OUTPUT_FILENAME)) as writer:
        df.to_excel(writer)

    pdf_file.close()


def run():

    # url = get_pdf_url()
    # print url
    # file = download_pdf(url)
    # print file
    file = 'input/lottery_results.pdf'
    read_pdf(file)

run()

print 'finis'


