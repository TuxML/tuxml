import requests


class APIManager:

    ADDRESS = "https://reqres.in/api/users"
    HEADERS = {
        'Content-type': 'application/json',
    }

    def __init__(self):
        self.address = ""
        self.headers = []

        self.setAddress(self.ADDRESS)
        self.setHeaders(self.HEADERS)

    def setAddress(self, address):
        self.address = address

    def setHeaders(self, headers):
        self.headers = headers

    def sendGet(self):
        return requests.get(self.address, self.headers)

    def sendPost(self, data):
        return requests.post(self.address, self.headers, data)

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