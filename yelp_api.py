from simple_settings import settings
import requests

class YelpAPI(object):

    def __init__(self, api_key):
        self._session = requests.Session()
        self._session.headers.update(self._get_auth_header(api_key))

    def make_api_request(self, params):

        params[]
        requests.get(self.url, params)
        pass

class YelpBusinessSearchAPI(YelpAPI):

    self.url = 'https://api.yelp.com/v3/businesses/search'

    def search(self, name):

