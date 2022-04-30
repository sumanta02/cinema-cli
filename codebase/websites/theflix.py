import sys
sys.path.append('..')

from ..httpclient import HttpClient
from bs4 import BeautifulSoup as bs
from ..util import get_theflix_cookie
import json
from colorama import Fore, Style

lmagenta = lambda a: f"{Fore.LIGHTMAGENTA_EX}{a}{Style.RESET_ALL}"


req = HttpClient()

k = get_theflix_cookie()



#some global shit
main_url = "https://theflix.to"
aux_url = "https://theflix.to:5679"

def fix_name(name):
    #list of special characters
    special_characters = ['!','@','#','$','%','^','&','*','(',')','_','+','=','{','}','[',']','|',':',';','"',"'",'<','>','?','/','\\','.',',','~']

    #remove special characters from name
    for i in special_characters:
        name = name.replace(i,'')
    
    return name.lower().replace(' ','-')
    
    

def search(ismovie,query):
    #function to search
    names = []
    ids = []
    seasons = []
    query = query.replace(' ', '+')
    
    if ismovie:
        search_url = f"{main_url}/movies/trending?search={query}"
        r=req.get(search_url)
        soup = bs(r.text,"html.parser")
        
        for i in json.loads(soup.select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"]:
            if(i["available"]):
                names.append(fix_name(i["name"]))
                ids.append(i["id"])
        
        return [list(sublist) for sublist in zip(names,ids)]
    
    else:
        search_url = f"{main_url}/tv-shows/trending?search={query}"
        
        r=req.get(search_url)
        soup = bs(r.text,"html.parser")
        for i in json.loads(soup.select("#__NEXT_DATA__")[0].text)["props"]["pageProps"]["mainList"]["docs"]:
            if(i["available"]):
                names.append(fix_name(i["name"]))
                ids.append(i["id"])
                seasons.append(i["numberOfSeason"])
                
        return [list(sublist) for sublist in zip(names,ids,seasons)]
    

def get_movie_link(id,name):
    url = f"{main_url}/movie/{id}-{name}"
    r=req.get(url)
    soup = bs(r.text,"html.parser")
    
    video_id = json.loads(soup.select('#__NEXT_DATA__')[0].text)['props']['pageProps']['movie']['videos'][0]

    
    link = req.get(f"{aux_url}/movies/videos/{video_id}/request-access?contentUsageType=Viewing",headers={"Cookie":k}).json()['url']
    print(link)
    return link

def get_show_link(id,name,seasons):
    season = input(lmagenta(f"Input the season number(total seasons:{seasons}): "))
    episodes = json.loads(
        bs(req.get(f"{main_url}/tv-show/{id}-{name}/season-{season}/episode-1",headers={'cookie':k}).text,"html.parser").select('#__NEXT_DATA__')[0].text)['props']['pageProps']['selectedTv']["seasons"][int(season)-1]['numberOfEpisodes']

    episode = input(lmagenta( f"Input the episode number(total episodes:{episodes}): "))
    
    #now get the episode id
    url = f"{main_url}/tv-show/{id}-{name}/season-{season}/episode-{episode}"
    r=req.get(url,headers={'cookie':k})
    soup = bs(r.text,"html.parser")
    f = json.loads(soup.select('#__NEXT_DATA__')[0].text)['props']['pageProps']['selectedTv']['seasons']
    epid = f[int(season)-1]['episodes'][int(episode)-1]['videos'][0]
    
    #now get the final streaming link
    link = req.get(f"{aux_url}/tv/videos/{epid}/request-access?contentUsageType=Viewing",headers={'cookie':k}).json()['url']
    
    return link



    

