'''
files as helper function
'''
from .httpclient import HttpClient
from bs4 import BeautifulSoup as bs
import yarl
import base64
import json
import regex

req = HttpClient()

#regex 
start_regex = regex.compile(r"#EXT-X-STREAM-INF(:.*?)?\n+(.+)")
res_regex = regex.compile(r"RESOLUTION=\d+x(\d+)")


def get_theflix_cookie():
    
    #helper function to get theflix cookie
    return req.post(
        "https://theflix.to:5679/authorization/session/continue?contentUsageType=Viewing",
        data={"affiliateCode": "","pathname": "/"}
        ).headers['Set-Cookie']


def get_token(link,key):
    #function to get gcaptcha token
    
    raw_domain = "https://rapid-cloud.ru:443"
    
    
    domain = base64.b64encode(raw_domain.encode()).decode().replace("\n", "").replace("=", ".") 

    r=req.get("https://www.google.com/recaptcha/api.js?render="+key,headers={'cacheTime':'0'})
    s=r.text.replace("/* PLEASE DO NOT COPY AND PASTE THIS CODE. */","")
    s=s.split(";")
    vtoken = s[10].replace("po.src=","").split("/")[-2]

    r=req.get("https://www.google.com/recaptcha/api2/anchor?ar=1&hl=en&size=invisible&cb=cs3&k="+key+"&co="+domain+"&v="+vtoken)
    soup = bs(r.content, "html.parser")
    recap_token = [i['value'] for i in soup.select("#recaptcha-token")][0]
    
    data = {
        "v" : vtoken,
        "k" : key,
        "c" : recap_token,
        "co" : domain,
        "sa" : "",
        "reason" :"q"
    }
    
    headers ={'cacheTime':'0'}
    
    j = json.loads(
        req.post("https://www.google.com/recaptcha/api2/reload?k="+key,data=data,headers=headers).text.replace(")]}'",'')
    )
    
    return j[1]
    


def get_m3u8_quality(link):
    
    
    links = []
    qualities = []
    
    partial_link = link[:link.rfind('/')+1]
    
    r=req.get(link)
    
    
    for i in start_regex.finditer(r.text):
        res_line,l = i.groups()
        
        #construct the quality 
        qualities.append(str(res_regex.search(res_line).group(1))+"p")
        
        #construct link
        links.append(partial_link+l.strip())
    
    return qualities,links
    