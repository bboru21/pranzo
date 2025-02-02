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
from collections import OrderedDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from simple_settings import settings


FIREFOX_DRIVER_PATH = '%s/geckodriver' % os.path.dirname(os.path.realpath(__file__))

URL = 'https://dcra.dc.gov/mrv'

HEADING = '%s MRV Location Lottery Results' % date.today().strftime('%B %Y') # e.g. October 2019
if settings.DEVELOPMENT and settings.DEVELOPMENT_HEADING:
    HEADING = settings.DEVELOPMENT_HEADING


def remove_file(file):
    if os.path.exists('%s' % file):
        os.remove('%s' % file)

def download_pdf(pdf_url):

    file = '%s%s' % (settings.INPUT_PATH, settings.INPUT_FILENAME)

    if settings.DEVELOPMENT:
        return file

    response = requests.get(pdf_url, stream=True)

    # remove old file if exists
    remove_file(file)

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

    if settings.DEVELOPMENT:
        return None

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
    Cleanup any data variants, such as certian vendor names ending in commas
    or foward slashes, which will screw up data processing later.
'''
def clean_lines(lines):
    clean_lines = []
    clean_line = ''

    previous = ''
    previous_trailing_comma = False

    try:
        # try and remove pesky heading column
        lines.remove(HEADING)
    except ValueError:
        print('WARNING: No HEADING \"%s\" was not found in %s. This may cause issues reading the data.' % (HEADING, settings.INPUT_FILENAME))

    for line in lines:
        line = line.rstrip()

        '''
            extractText unable to decode L'Enfants right single quote, so it
            translates it to a blank string. Add it back here:
        '''
        line = 'L\'Enfant' if line == '' else line

        last_index = len(clean_lines)-1

        if previous_trailing_comma:
            clean_lines[last_index] = '%s %s' % (clean_lines[last_index], line)
        else:
            clean_lines.append(line)

        previous_trailing_comma = ( line.endswith(',') or line.endswith('/') )

    clean_lines = clean_lines[7:] # remove columns

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

    if name == 'OFF':
        return None

    invalid_excel_chars = re.compile(r'[\[\]\:\*\?\\/]')
    return re.sub(invalid_excel_chars, ' ', name)

def insert_vendor(site_permit, business_name):
    if settings.USE_DATABASE:
        # include models import here for now so we don't create if user doesn't want
        from models import Vendor

        engine = create_engine(settings.DATABASES['ENGINE'])

        if engine.dialect.has_table(engine, 'vendor'):
            Session = sessionmaker(bind=engine)
            session = Session()

            insert = {
                "site_permit": site_permit,
                "name": business_name
            }

            vendor = session.query(Vendor).filter_by(site_permit=site_permit).first()
            if not vendor:
                vendor = Vendor(**insert)
                session.add(vendor)

            session.commit()


'''
    Takes chunked data, and puts it into more readable format for consumer purposes
'''
def process_data(data):

    processed_data = {}

    for business_data in data:

        site_permit = business_data[0]
        business_name = business_data[1]
        weekly_schedule = business_data[2:]

        insert_vendor(site_permit, business_name)

        d = 0
        for day in weekly_schedule:
            dow = get_dow(d)
            location = day
            location = clean_location_name(location)

            if location:

                if location not in processed_data:
                    processed_data[location] = {
                        'Monday': [],
                        'Tuesday': [],
                        'Wednesday': [],
                        'Thursday': [],
                        'Friday': [],
                    }

                processed_data[location][dow].append(business_name)

            d += 1

    return processed_data

def read_pdf():

    file = '%s%s' % (settings.INPUT_PATH, settings.INPUT_FILENAME)

    # TODO logic may need to be updated from time to time due to pdf formatting
    pdf_file = open(file, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file, strict=False)

    data = process_pages(pdf_reader)
    data = process_data(data)

    pdf_file.close()

    return data

'''
    Pandas needs all lists within spreadsheet to be of same length, so pad
    lists with blank values to prevent ValueError Arrays Must be All Same
    Length exceptions.

    https://stackoverflow.com/questions/40442014/python-pandas-valueerror-arrays-must-be-all-same-length
'''
def pad_dict_list(dict_list, padel):
    lmax = 0
    for lname in dict_list.keys():
        lmax = max(lmax, len(dict_list[lname]))
    for lname in dict_list.keys():
        ll = len(dict_list[lname])
        if  ll < lmax:
            dict_list[lname] += [padel] * (lmax - ll)
    return dict_list

def write_to_excel(data):
    if settings.DEVELOPMENT:
        return False

    file = '%s%s' % (settings.OUTPUT_PATH, settings.OUTPUT_FILENAME)
    remove_file(file) # remove old file if exists
    writer = pd.ExcelWriter(file, engine='xlsxwriter')
    for location, location_schedule in data.items():
        location_schedule = pad_dict_list( location_schedule, '' )
        df = pd.DataFrame(location_schedule)
        df.to_excel(writer, sheet_name=location)
    writer.save()


def run():

    url = get_pdf_url()
    download_pdf(url)
    data = read_pdf()
    write_to_excel(data)

    print( 'Schedule for %s has been downloaded to %s%s' % (HEADING, settings.OUTPUT_PATH, settings.OUTPUT_FILENAME))

run()

print( 'finis' )


