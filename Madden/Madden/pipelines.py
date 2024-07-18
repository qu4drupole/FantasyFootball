# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import os

class MaddenPipeline:
    base_dir = "/Users/smithd30/personal/FF/Madden/"
    def process_item(self, item, spider):
        if spider.name == "boxscores":
            # passing
            if not os.path.isfile(self.base_dir+"pass.csv"):
                item["pass"].reset_index().to_csv(self.base_dir+"pass.csv")
            else:
                pass_dat = pd.read_csv(self.base_dir+"pass.csv", index_col=0)
                pass_dat = pd.concat([pass_dat, item["pass"].reset_index()], ignore_index=True)
                pass_dat.to_csv(self.base_dir+"pass.csv")
            # rushing
            if not os.path.isfile(self.base_dir+"rush.csv"):
                item["rush"].reset_index().to_csv(self.base_dir+"rush.csv")
            else:
                rush_dat = pd.read_csv(self.base_dir+"rush.csv", index_col=0)
                rush_dat = pd.concat([rush_dat, item["rush"].reset_index()], ignore_index=True)
                rush_dat.to_csv(self.base_dir+"rush.csv")
            # receiving
            if not os.path.isfile(self.base_dir+"receiving.csv"):
                item["rec"].reset_index().to_csv(self.base_dir+"receiving.csv")
            else:
                rec_dat = pd.read_csv(self.base_dir+"receiving.csv", index_col=0)
                rec_dat = pd.concat([rec_dat, item["rec"].reset_index()], ignore_index=True)
                rec_dat.to_csv(self.base_dir+"receiving.csv")
            # defense
            if not os.path.isfile(self.base_dir+"defense.csv"):
                item["defense"].to_csv(self.base_dir+"defense.csv")
            else:
                def_dat = pd.read_csv(self.base_dir+"defense.csv", index_col=0)
                def_dat = pd.concat([def_dat, item["defense"]], ignore_index=True)
                def_dat.to_csv(self.base_dir+"defense.csv")

        elif spider.name == "fantasyscores":
            if not os.path.isfile(self.base_dir+"ffscores.csv"):
                item['res'].to_csv(self.base_dir+"ffscores.csv")
            else:
                ff_dat = pd.read_csv(self.base_dir+"ffscores.csv", index_col=0)
                ff_dat = pd.concat([ff_dat, item['res']], ignore_index=True)
                ff_dat.to_csv(self.base_dir+"ffscores.csv")

        return None