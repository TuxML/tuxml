import requests


class APIManager:

    DEFAULT_API_ADDRESS = "https://reqres.in/api/users"

    DEFAULT_HEADERS = {
        'Content-type': 'application/json',
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

    def sendPost(self, data):
        return requests.post(self.address, headers=self.headers, auth=self.auth, params=self.params, data=data)

# TEST A SUPPRIMER
apiManager = APIManager()

print("\n*************\nTest GET :\n*************")

response = apiManager.sendGet()

print(response)
print(response.json())

print("\n*************\nTest POST :\n*************")

data = '{ "name": "lea", "job": "mia" }'
response = apiManager.sendPost(data)

print(response)
print(response.json())
print()