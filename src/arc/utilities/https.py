from http.client import HTTPSConnection

from arc import Utility

https = Utility("https")


@https.script("get")
def get(url, endpoint):
    conn = HTTPSConnection(url)
    conn.request("GET", endpoint)
    response = conn.getresponse()
    print(response.read())
    conn.close()
