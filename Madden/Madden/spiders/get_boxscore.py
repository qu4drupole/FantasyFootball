from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import scrapy
import ssl
import re

class boxscoreSpider(scrapy.Spider):
    name = "boxscores"
    ssl._create_default_https_context = ssl._create_unverified_context
    weekn=0

    team_dict = {"Detroit Lions":"det","Kansas City Chiefs":"kc","Carolina Panthers":"car","Atlanta Falcons":"atl","Houston Texans":"hou","Baltimore Ravens":"bal",
    "Cincinnati Bengals":"cin","Cleveland Browns":"cle","Jacksonville Jaguars":"jax","Indianapolis Colts":"ind","Tampa Bay Buccaneers":"tb","Minnesota Vikings":"min","Tennessee Titans":"ten","New Orleans Saints":"no",
    "San Francisco 49ers":"sf","Pittsburgh Steelers":"pit","Arizona Cardinals":"ari","Washington Commanders":"was","Green Bay Packers":"gb","Chicago Bears":"chi","Las Vegas Raiders":"lv","Denver Broncos":"den",
    "Miami Dolphins":"mia","Los Angeles Chargers":"lac","Philadelphia Eagles":"phi","New England Patriots":"ne","Los Angeles Rams":"lar","Seattle Seahawks":"sea","Dallas Cowboys":"dal","New York Giants":"nyg",
    "Buffalo Bills":"buf","New York Jets":"nyj"}

    start_urls = [
        # "https://sportsdata.usatoday.com/football/nfl/scores",
        # "https://sportsdata.usatoday.com/football/nfl/scores?season=2023&type=Week%206",
        "https://sportsdata.usatoday.com/football/nfl/scores?season=2023&type=Week%2016"
    ]

    def parse(self, response):
        weekn = int(re.search("Week\%20(\d*)", response.url).group(1))
        soup = BeautifulSoup(response.body, 'html.parser')
        base_url = response.url.split("?")[0]
        for g in soup.find_all("div", class_="class-37RyWMg"):
            # check whether game is finished
            # if 'FINAL' in g.find("p", class_="class-urWQNRe class-8ygQElb").text:
            #     # gather the week # and teams
            # week_n = g.find("span", class_="class--Gl-eps").text
            # teams = []
            # for team in g.find_all("span", class_="class-jer7RpM"):
            #     teams.append(team.text)
            # yield {
            #     "week":week_n,
            #     "teams":teams
            # }
            # get the box score link
            for l in g.find_all("a"):
                if l.text == "Box Score":
                    # game_id = l.get("href").split("/")[-1]
                    # game_url = response.urljoin(game_id)
                    # game_url = base_url + "/" + game_id
                    # scrapy.Request(game_url, self.parse_boxes)
                    game_id = l.get("href")
                    yield response.follow(game_id, self.parse_boxes, cb_kwargs={"weekn":weekn})
                    

    def parse_boxes(self, response, weekn):
        soup = BeautifulSoup(response.body, 'html.parser')
        res = pd.read_html(response.url, index_col=0)
        # Some basic stats
        # t_home = res[0].index[1].lower()
        # t_away = res[0].index[0].lower() # they updated their layout 
        teams = soup.find_all('span', class_="class-HNamaZP class-FGnXvyV")
        t_away = self.team_dict[teams[0].text]
        t_home = self.team_dict[teams[1].text]

        # Passing
        pass_home = res[1]
        pass_home['opp'] = t_away
        pass_away = res[0]
        pass_away['opp'] = t_home
        pass_df = pd.concat([pass_home, pass_away])
        pass_df['weekn'] = weekn

        # Rushing
        rush_home = res[3]
        rush_home['opp'] = t_away
        rush_away = res[2]
        rush_away['opp'] = t_home
        rush_df = pd.concat([rush_home, rush_away])
        rush_df['weekn'] = weekn

        # Receiving
        rec_home = res[5]
        rec_home['opp'] = t_away
        rec_away = res[4]
        rec_away['opp'] = t_home
        rec_df = pd.concat([rec_home, rec_away])
        rec_df['weekn'] = weekn

        # Defense
        def_home = res[13].loc[:,["Total","Sack", "Int", "PD", "FF"]].sum()
        def_home['team'], def_home['opp'], def_home['weekn'], def_home['home'] = t_home, t_away, weekn, 1
        # def_home['points'] = res[0].loc[res[0].index[0], "T"]
        def_home['points'] = int(soup.find('div', class_="class-Kvlo2AF").contents[1].find('span').text)
        def_home_pass = pass_away[['Comp', "Att", "Yds", "TD"]].sum()
        def_home_pass.index = ['pass_'+stat for stat in def_home_pass.index.tolist()]
        def_home_rush = rush_away[['Rush',  'Yds', 'Avg', 'TD']].sum()
        def_home_rush.index = ['rush_'+stat for stat in def_home_rush.index.tolist()]
        def_home_rec = rec_away[['Rec', 'Yds', 'Avg']].sum()
        def_home_rec.index = ['rec_'+stat for stat in def_home_rec.index.tolist()]
        def_home = pd.concat([def_home, def_home_pass, def_home_rush, def_home_rec])

        def_away = res[12].loc[:,["Total","Sack", "Int", "PD", "FF"]].sum()
        def_away['team'], def_away['opp'], def_away['weekn'], def_away['home'] = t_away, t_home, weekn, 0
        # def_away['points'] = res[0].loc[res[0].index[1], "T"]
        def_away['points'] = int(soup.find('div', class_="class--7rEKKD").find('span').text)
        def_away_pass = pass_home[['Comp', "Att", "Yds", "TD"]].sum()
        def_away_pass.index = ['pass_'+stat for stat in def_away_pass.index.tolist()]
        def_away_rush = rush_home[['Rush',  'Yds', 'Avg', 'TD']].sum()
        def_away_rush.index = ['rush_'+stat for stat in def_away_rush.index.tolist()]
        def_away_rec = rec_home[['Rec', 'Yds', 'Avg']].sum()
        def_away_rec.index = ['rec_'+stat for stat in def_away_rec.index.tolist()]
        def_away = pd.concat([def_away, def_away_pass, def_away_rush, def_away_rec])

        def_all = pd.concat([def_home, def_away], axis=1).T

        yield {
            "pass":pass_df,
            "rush":rush_df,
            "rec":rec_df,
            "defense":def_all
        }