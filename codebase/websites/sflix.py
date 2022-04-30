import sys


sys.path.append('..')

from ..httpclient import HttpClient
from bs4 import BeautifulSoup as bs
import re
from ..util import get_token,get_m3u8_quality
from colorama import Fore, Style

lmagenta = lambda a: f"{Fore.LIGHTMAGENTA_EX}{a}{Style.RESET_ALL}"

req= HttpClient()

#some global shit
main_url = "https://sflix.se"


def search(query):
    #search function
    query = query.replace(" ","-")
    search_url = f"{main_url}/search/{query}"
    r=req.get(search_url).text


def render(ismovie,r):
    soup = bs(r,"html.parser")
    
    if ismovie:
        titles = [i["title"] for i in soup.select(".film-poster a") if i["href"].__contains__('/movie/')]
        links = [i["href"].split("-")[-1] for i in soup.select(".film-poster a") if i["href"].__contains__('/movie/')]
        
        return list(zip(titles,links))
    else:
        titles = [i["title"] for i in soup.select(".film-poster a") if i["href"].__contains__('/tv/')]
        links = [i["href"].split("-")[-1] for i in soup.select(".film-poster a") if i["href"].__contains__('/tv/')]
        return list(zip(titles,links))
    
def get_movie_server(movie_id):
    r = req.get(f"{main_url}/ajax/movie/episodes/{movie_id}").text
    soup = bs(r,'html.parser')
    return [i['data-id'] for i in soup.select('.link-item')][0]

def get_season_episode(sid):
    #function to get seasons and episdoe id
    season_url = f"{main_url}/ajax/v2/tv/seasons/{sid}"
    r=req.get(season_url)
    
    season_ids = [i['data-id'] for i in bs(r.text,'html.parser').select(".dropdown-item")]
    
    s = int(input(lmagenta(f"Enter the season number({len(season_ids)}): ")))
    
    episode_url = f"{main_url}/ajax/v2/season/episodes/{season_ids[s-1]}"
    r=req.get(episode_url)
    episodes = [i['data-id'] for i in bs(r.text,'html.parser').select(".episode-item")]
    
    e=int(input(lmagenta(f"Enter the episode number({len(episodes)}): ")))
    return episodes[e-1]
    

def get_show_server(show_id):
    #after getting the season and episdoes
    r = req.get(f"{main_url}/ajax/v2/episode/servers/{show_id}/#servers-list").text
    soup = bs(r,'html.parser')
    return [i['data-id'] for i in soup.select('.link-item')][0]    
    
def generate_final_link(server_id,m_url=""):
    
    #use this after gettihg the server id
    if(len(m_url)==0):
        m_url = main_url
        
    #print(f"{m_url}/ajax/get_link/{server_id}")
    
    link=req.get(f"{m_url}/ajax/get_link/{server_id}").json()['link']
    
    #get the number and key from the rabbid link and the rabbid id
    rabbit_id = link.split("/")[-1].split("?")[0]
    
    r=req.get(link,headers={"Referer":f"{m_url}/"})
    soup = bs(r.content,'html.parser')
    num = [i.text for i in soup.find_all("script")][-3].replace("var","")
    x=str(num).split(",")
    key=x[0].split("= ")[-1].replace("'","")
    times=x[1].split("= ")[-1].replace("'","")
    
    token = get_token(link,key)
    
    #final request
    x = req.get(f"https://rabbitstream.net/ajax/embed-4/getSources?id={rabbit_id}&_token={token}&_number={times}",headers={'X-Requested-With': 'XMLHttpRequest'}).json()
    
    languages = [x["tracks"][i]["label"] for i in range(len(x["tracks"])-1)]        
    subtitles = [x["tracks"][i]["file"] for i in range(len(x["tracks"])-1)]
    
    subs = [list(sublist) for sublist in zip(languages,subtitles)]
    '''
    final link part
    '''
    final_link = x["sources"][0]["file"]
    
    
    qualities,links = get_m3u8_quality(final_link)
    q=[list(qlist) for qlist in zip(qualities,links)]    
    
    return subs,q  
    
        
    
    