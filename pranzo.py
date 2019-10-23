# -*- coding: UTF-8 -*-
import os
import sys
from selenium import (
    webdriver,
    common as selenium_common
)
import requests
import PyPDF2
import pandas as pd
import backoff
import re
from datetime import date

FIREFOX_DRIVER_PATH = '%s/geckodriver' % os.path.dirname(os.path.realpath(__file__))

INPUT_PATH = 'input/'
INPUT_FILENAME = 'lottery_results.pdf'
URL = 'https://dcra.dc.gov/mrv'

OUTPUT_PATH = 'output/'
OUTPUT_FILENAME = 'lottery_results.xlsx'

HEADING = '%s MRV Location Lottery Results' % date.today().strftime('%B %Y') # e.g. October 2019

SCHEDULE = {
    'Monday': [],
    'Tuesday': [],
    'Wednesday': [],
    'Thursday': [],
    'Friday': [],
}


def download_pdf(pdf_url):
    file = '%s%s' % (INPUT_PATH, INPUT_FILENAME)
    response = requests.get(pdf_url, stream=True)

    with open(file,"wb+") as pdf:
        for chunk in response.iter_content(chunk_size=1024):
             if chunk:
                 pdf.write(chunk)

    return file

# sometimes initial request produces "Secure Connection Failed" - PR_END_OF_FILE_ERROR
@backoff.on_exception(
    backoff.expo,
    selenium_common.exceptions.WebDriverException,
    max_tries=3,
    jitter=None
)
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

'''
    Some vendors names have commas and carriage returns, which screws up the readability.
'''
def clean_lines(lines):
    clean_lines = []
    clean_line = ''

    previous = ''
    previous_trailing_comma = False

    for line in lines:
        line = line.rstrip()

        last_index = len(clean_lines)-1

        if previous_trailing_comma:
            clean_lines[last_index] = '%s %s' % (clean_lines[last_index], line)
        else:
            clean_lines.append(line)

        previous_trailing_comma = line.endswith(',')

    return clean_lines

def process_pages(pdf_reader):
    data = []
    num_pages = pdf_reader.numPages

    i = 0
    while i < num_pages:
        page = pdf_reader.getPage(i)
        text  = page.extractText()
        lines = text.splitlines()

        lines = clean_lines(lines)
        try:
            # try and remove pesky heading column
            lines.remove(HEADING)
        except ValueError:
            pass

        lines = ['L\'Enfant' if line == '' else line for line in lines] # correct encoding issue with right single quote
        lines = lines[7:] # remove columns

        lines = list(divide_chunks(lines, 7))

        data = data + lines

        i = i+1
    return data

def get_dow(d):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    return days[d]

'''
    Remove invalid excel sheetname characters from location name so we can use
    it for the sheetname later.
'''
def clean_location_name(name):
    invalid_excel_chars = re.compile(r'[\[\]\:\*\?\\/]')
    return re.sub(invalid_excel_chars, ' ', name)

'''
    Takes chunked data, and puts it into more readable format for consumer purposes
'''
def process_data(data):

    processed_data = {}

    for business_data in data:

        site_permit = business_data[0]
        business_name = business_data[1]
        weekly_schedule = business_data[2:]

        d = 0
        for day in weekly_schedule:
            dow = get_dow(d)
            location = day
            location = clean_location_name(location)

            if location not in processed_data:
                processed_data[location] = {}

            if dow not in processed_data[location]:
                processed_data[location][dow] = []

            processed_data[location][dow].append(business_name)

            d += 1

    return processed_data

def read_pdf(file):
    # TODO logic may need to be updated from time to time due to pdf formatting
    pdf_file = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file, strict=False)

    data = process_pages(pdf_reader)
    data = process_data(data)

    writer = pd.ExcelWriter('%s%s' % (OUTPUT_PATH, OUTPUT_FILENAME), engine='xlsxwriter')
    for location, location_schedule in data.items():
        df = pd.DataFrame(location_schedule)
        df.to_excel(writer, sheet_name=location)
    writer.save()

    pdf_file.close()


def run():

    url = get_pdf_url()
    # print( url )
    file = download_pdf(url)
    # print( file )
    # file = 'input/lottery_results.pdf'
    read_pdf(file)
    print( 'Schedule for %s has been downloaded to %s%s' % (HEADING, OUTPUT_PATH, OUTPUT_FILENAME))

run()

print( 'finis' )


