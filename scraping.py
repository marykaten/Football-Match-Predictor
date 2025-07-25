import cloudscraper
import pandas as pd
import time
from bs4 import BeautifulSoup
from io import StringIO

scraper = cloudscraper.create_scraper()
standing_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

html = scraper.get(standing_url).text
soup = BeautifulSoup(html, 'html.parser')
standings_table = soup.select('table.stats_table')[0]

links = standings_table.find_all('a')
links = [l.get('href') for l in links]
links = [l for l in links if '/squads/' in l]

team_urls = [f"https://fbref.com{l}" for l in links]
team_url = team_urls[0]

data = scraper.get(team_url).text
soup = BeautifulSoup(data, 'html.parser')
team_stats = pd.read_html(StringIO(str(soup)))[1]

links = soup.find_all('a')
links = [l.get('href') for l in links]
links = [l for l in links if l and 'all_comps/shooting/' in l]

shooting_data_url = f"https://fbref.com{links[0]}"
shooting_data = scraper.get(shooting_data_url).text

shooting_stats = pd.read_html(StringIO(shooting_data))[0]
shooting_stats.columns = shooting_stats.columns.droplevel()

team_data = team_stats.merge(shooting_stats[["Date","Sh","SoT","Dist","FK","PK","PKatt"]])
