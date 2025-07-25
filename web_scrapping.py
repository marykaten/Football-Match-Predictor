import cloudscraper
import pandas as pd
import time
from bs4 import BeautifulSoup
from io import StringIO

scraper = cloudscraper.create_scraper()
standing_url = "https://fbref.com/en/comps/9/Premier-League-Stats"

years = list(range(2025,2023,-1))

all_matches = []
for year in years:
    html = scraper.get(standing_url).text
    soup = BeautifulSoup(html, 'html.parser')
    standings_table = soup.select('table.stats_table')[0]

    links = [l.get('href') for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"

    for team_url in team_urls:
        team_name = team_url.split('/')[-1].replace("-Stats","")

        data = scraper.get(team_url).text
        soup = BeautifulSoup(data, 'html.parser')
        team_stats = pd.read_html(StringIO(str(soup)))[1]

        links = [l.get('href') for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = f"https://fbref.com{links[0]}"
        shooting_data = scraper.get(data).text
        shooting_stats = pd.read_html(StringIO(shooting_data))[0]
        shooting_stats.columns = shooting_stats.columns.droplevel()

        try:
            team_data = team_stats.merge(shooting_stats[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]])
        except ValueError:
            continue

        team_data = team_data[team_data["Comp"] == "Premier League"]
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(1)

match_df = pd.concat(all_matches)
match_df.to_csv("matches.csv")
