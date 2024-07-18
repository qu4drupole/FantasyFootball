from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import scrapy
import ssl
import re

# for rotoballer, all scoring assumes 6 points for QB touchdowns, rather than 4

class ffSpider(scrapy.Spider):
    name = "fantasyscores"
    # ssl._create_default_https_context = ssl._create_unverified_context
    weekn=0

    start_urls = [
        # "https://www.rotoballer.com/nfl-game-center-live-scores-fantasy-football-scoreboard?week=6",
        "https://www.rotoballer.com/nfl-game-center-live-scores-fantasy-football-scoreboard?week=16"
    ]

    def parse(self, response):
        self.weekn = int(re.search("week.(\d*)", response.url).group(1))
        ff = pd.read_html(response.body)
        tbl = ff[0]
        names = tbl['Player'].apply(lambda x: x.split("(")[0].strip())
        tbl['Name'] = names
        meta = tbl.apply(lambda x: re.search("\((.*)\)", x["Player"]).group(1).split(","), axis=1, result_type='expand')
        meta.columns = ['pos','team']
        meta["team"] = meta["team"].apply(lambda x: x.lower())
        tbl = tbl.join(meta)
        tbl['weekn'] = self.weekn
        tbl = tbl.loc[:,~tbl.columns.str.contains("Unnamed")]
        tbl.loc[tbl["pos"]=="QB", "PPR PTS"] = tbl.loc[tbl["pos"]=="QB", "PPR PTS"] - 2*tbl.loc[tbl["pos"]=="QB", "TD"]
        yield {
            "res":tbl
        }