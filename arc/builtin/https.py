from http.client import HTTPSConnection

from arc import namespace

https = namespace("https")


@https.subcommand()
def get(url, endpoint):
    conn = HTTPSConnection(url)
    conn.request("GET", endpoint)
    response = conn.getresponse()
    print(response.read())
    conn.close()
