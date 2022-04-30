# A simple http client

import httpx

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"

#create a httpclient class
class HttpClient:
    def __init__(self, headers = user_agent):
        self.session = httpx.Client(headers ={'User-Agent': user_agent})
        
    # a get request method
    def get(self, url,headers={},params={},cookies={}):
        return self.session.get(url, headers=headers, params=params,cookies=cookies)
    
    #a post request method
    def post(self, url, data={}, headers={},cookies={}):
        return self.session.post(url, data=data,cookies=cookies, headers=headers)
    
        
        
        