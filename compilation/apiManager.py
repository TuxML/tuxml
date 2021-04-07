import requests

class APIManager:

    TOKEN = "tokenwrite4jeHmRkh7R"

    DEFAULT_API_ADDRESS = "https://tuxmlweb.istic.univ-rennes1.fr/api/v0/uploadResults"

    DEFAULT_HEADERS = {
        'Content-type': 'application/json',
        'authorization': 'Bearer '+TOKEN
    }

    DEFAULT_AUTH = None
    # Example :
    # ('username', 'password')

    DEFAULT_PARAMS = None
    # Example :
    # DEFAULT_PARAMS = (
    #     ('key', 'mykeyhere'),
    # )

    def __init__(self):
        self.address = ""
        self.headers = []
        self.auth = []
        self.params = []

        self.setAddress(self.DEFAULT_API_ADDRESS)
        self.setHeaders(self.DEFAULT_HEADERS)
        self.setAuth(self.DEFAULT_AUTH)
        self.setParams(self.DEFAULT_PARAMS)

    def setAddress(self, address):
        self.address = address

    def setHeaders(self, headers):
        self.headers = headers
    
    def setAuth(self, auth):
        self.auth = auth

    def setParams(self, params):
        self.params = params

    def sendGet(self):
        return requests.get(self.address, headers=self.headers, auth=self.auth, params=self.params)

    def sendPost(self, json):
        return requests.post(self.address, headers=self.headers, auth=self.auth, params=self.params, json=json)