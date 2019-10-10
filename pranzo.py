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

FIREFOX_DRIVER_PATH = '%s/geckodriver' % os.path.dirname(os.path.realpath(__file__))

INPUT_PATH = 'input/'
INPUT_FILENAME = 'lottery_results.pdf'
URL = 'https://dcra.dc.gov/mrv'

OUTPUT_PATH = 'output/'
OUTPUT_FILENAME = 'lottery_results.xlsx'

HEADING = 'October 2019 MRV Location Lottery Results' # TODO month/year need to be dynamic
DESIRED_LOCATION = 'Georgetown'
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
    max_tries=2,
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

def update_schedule_by_location(current_list):

    global SCHEDULE

    for item in current_list:
        if DESIRED_LOCATION in item:
            new_item_list = []

            i = 0
            for column in item[1:]:

                if i == 0:
                    name = column
                else:
                    if column == DESIRED_LOCATION:
                        if i == 1: dow = 'Monday'
                        elif i == 2: dow = 'Tuesday'
                        elif i == 3: dow = 'Wednesday'
                        elif i == 4: dow = 'Thursday'
                        elif i == 5: dow = 'Friday'

                        SCHEDULE[dow].append(name)
                i += 1


def read_pdf(file):
    # TODO logic may need to be updated from time to time due to pdf formatting
    pdf_file = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    num_pages = pdf_reader.numPages

    i = 0
    while i < num_pages:
        page = pdf_reader.getPage(i)
        text = page.extractText()
        lines = text.splitlines()

        lines.remove(HEADING)
        lines.remove('')
        lines = lines[6:] # remove month and columns
        lines = list(divide_chunks(lines, 7))
        update_schedule_by_location(lines)

        i = i+1

    df = pd.DataFrame(SCHEDULE)
    with pd.ExcelWriter('%s%s' % (OUTPUT_PATH, OUTPUT_FILENAME)) as writer:
        df.to_excel(writer)

    pdf_file.close()


def run():

    url = get_pdf_url()
    # print url
    file = download_pdf(url)
    # print file
    # file = 'input/lottery_results.pdf'
    read_pdf(file)
    print 'Schedule for %s has been downloaded to %s%s' % (DESIRED_LOCATION, OUTPUT_PATH, OUTPUT_FILENAME)

run()

print 'finis'


