import sys


sys.path.append('..')

from ..httpclient import HttpClient
from bs4 import BeautifulSoup as bs
from .sflix import render,generate_final_link
from colorama import Fore, Style

lmagenta = lambda a: f"{Fore.LIGHTMAGENTA_EX}{a}{Style.RESET_ALL}"

req= HttpClient()

#some global shit
main_url = "https://solarmovie.pe/"


def search(query):
    #search function
    query = query.replace(" ","-")
    search_url = f"{main_url}/search/{query}"
    r=req.get(search_url).text

def get_movie_server(movie_id):
    r = req.get(f"{main_url}/ajax/movie/episodes/{movie_id}").text
    soup = bs(r,'html.parser')
    return [i['data-linkid'] for i in soup.select('.nav-item a')][0]

def get_season_episode(sid):
    #function to get seasons and episdoe id
    season_url = f"{main_url}/ajax/v2/tv/seasons/{sid}"
    r=req.get(season_url)
    
    season_ids = [i['data-id'] for i in bs(r.text,'html.parser').select(".dropdown-item")]
    
    s = int(input(lmagenta(f"Enter the season number({len(season_ids)}): ")))
    
    episode_url = f"{main_url}/ajax/v2/season/episodes/{season_ids[s-1]}"
    r=req.get(episode_url)
    episodes = [i['data-id'] for i in bs(r.text,'html.parser').select("a")]
    
    e=int(input(lmagenta(f"Enter the episode number({len(episodes)}): ")))
    return episodes[e-1]

def get_show_server(show_id):
    #after getting the season and episdoes
    r = req.get(f"{main_url}/ajax/v2/episode/servers/{show_id}/#servers-list").text
    soup = bs(r,'html.parser')
    return [i['data-id'] for i in soup.select('.link-item')][0]

