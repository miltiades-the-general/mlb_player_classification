from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from bs4 import Comment

class ScrapePlayerData:
    def __init__(self):
        self = self
        # url and endpoint
        self.homepage_url = "https://www.baseball-reference.com/"
        self.atbats_page = "leaders/AB_career.shtml"

    def collect_player_links(self):
        # returns a response page with the at bats leaders 
        # parse through the <tr> tags which holds the table contents
        response = requests.get(self.homepage_url + self.atbats_page)
        soup = BeautifulSoup(response.content, "html.parser")
        tr = soup.find_all("tr")

        new_soup = BeautifulSoup(str(tr), "html.parser")

        a_tags = new_soup.find_all("a", href=True)
        player_links = []

        # Returns a list of url endpoints for players with the most career at bats
        for a in a_tags:
            player_links.append(a["href"])
        return player_links
    
    def scrape_player_name(self, player_endpoint):
        response = requests.get(self.homepage_url + player_endpoint)
        soup = BeautifulSoup(response.content, "html.parser")
        name_div = soup.find("div", id="meta")
        h1 = name_div.find_all("h1")[0]
        span = h1.find("span")
        name = span.contents[0]
        return name

    def scrape_statistic_tables(self, player_endpoint):
        # Request the player page
        # Parse through the stats tables of the player page
        response = requests.get(self.homepage_url + player_endpoint)
        soup = BeautifulSoup(response.content, "html.parser")
        standard_batting = soup.find("div", id="div_batting_standard")
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        new_soup = BeautifulSoup(str(comments))
        value = new_soup.find("div", id="div_batting_value")
        advanced = new_soup.find("div", id="div_batting_advanced")

        # player value is parsed and written into a dataframe
        # it has a multilevel index and we only care about the first layer or 0th index
        # we drop duplicate years which means that the player played for more than one team, the yearly total stats are preserved
        value_df = pd.read_html(str(value))
        value_df = value_df[0]
        value_df = value_df.drop_duplicates("Year").reset_index()

        # the advanced statistics are parsed and written into a dataframe 
        # similarly we take the 0th index but we also drop a level on this dataframe
        # we take until the -3 row 
        advanced_df = pd.read_html(str(advanced))
        advanced_df = advanced_df[0]
        advanced_df = advanced_df.droplevel(0, axis=1)
        advanced_df = advanced_df[:-3].drop_duplicates("Year").reset_index()

        # the standard batting statistics are parsed and written into a dataframe
        # we take the 0th index of the return
        # we drop duplicate years
        standard_batting = str(standard_batting)
        standard_batting_df = pd.read_html(standard_batting)
        standard_batting_df = standard_batting_df[0]
        standard_batting_df = standard_batting_df.drop_duplicates("Year").reset_index()

        # we merge the three dataframes in 2 subsequent merges 
        merged_df = standard_batting_df.merge(advanced_df, on="Year")
        merged_df = merged_df.merge(value_df, on="Year")
        merged_df = merged_df.drop_duplicates("Year")[:-1].reset_index().drop(["index_x"], axis=1)
        return merged_df 


def main():
    scrape = ScrapePlayerData()
    links = scrape.collect_player_links()
    count = 0
    end = 5
    df_list = []
    name_list = [] 

    while count <= end:
        for link in links:
            df = scrape.scrape_statistic_tables(link)
            name = scrape.scrape_player_name(link)
            name_list.append(name)
            df_list.append(df)
            time.sleep(.5)
        count += 1
    


if __name__ == "__main__":
    main()
