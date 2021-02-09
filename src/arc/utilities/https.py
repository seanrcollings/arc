from http.client import HTTPSConnection

from arc import group

https = group("https")


@https.subcommand()
def get(url, endpoint):
    conn = HTTPSConnection(url)
    conn.request("GET", endpoint)
    response = conn.getresponse()
    print(response.read())
    conn.close()
