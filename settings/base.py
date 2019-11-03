USE_DATABASE = False
DATABASES = {
    'ENGINE': 'sqlite:///db/pranzodb.db'
}

INPUT_PATH = 'input/'
INPUT_FILENAME = 'lottery_results.pdf'

OUTPUT_PATH = 'output/'
OUTPUT_FILENAME = 'lottery_results.xlsx'

DEVELOPMENT = False # prevents url request and writing of files for easier development
