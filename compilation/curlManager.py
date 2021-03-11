import requests


class CurlManager:

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

    def test(self):
        print("Test GET :")
        response = self.sendGet()
        print(response)
        print(response.json())

        print("Test POST :")
        data = '{ "name": "lea", "job": "mia" }'
        response = self.sendPost(data)
        print(response)
        print(response.json())


curlManager = CurlManager()
curlManager.test()
