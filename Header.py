import urllib.request
from fake_headers import Headers
from bs4 import BeautifulSoup
from random import randint


#Creates a randomized header with a proxy ip and a fake user agent
class Header:

    def __init__(self):
        self.proxies = []

    def get_proxy_ips(self, header):
        proxies_request = urllib.request.Request('https://www.sslproxies.org/', headers=header)
        open = urllib.request.urlopen(proxies_request).read().decode('utf8')

        soup = BeautifulSoup(open, 'html.parser')
        proxies_table = soup.find(id='proxylisttable')

        proxies = []
        for row in proxies_table.tbody.find_all('tr'):
            proxies.append({
                'ip': row.find_all('td')[0].string,
                'port': row.find_all('td')[1].string
            })

        return proxies


    def create_header(self):
        user_agent = Headers(headers=True).generate()['User-Agent']
        header = {'User-Agent': user_agent}

        if len(self.proxies) == 0:
             self.proxies = self.get_proxy_ips(header)

        proxy = self.proxies[randint(0, len(self.proxies) - 1)]

        header["Proxy"] = proxy.get("ip") + ":" + proxy.get("port")
        return header


