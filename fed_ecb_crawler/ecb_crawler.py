from fed_ecb_crawler.crawler_base import CrawlerBase, ArticleModel
import requests
from bs4 import BeautifulSoup, Tag
import re
import os
from datetime import datetime


class ECBCrawler(CrawlerBase):
    def __init__(self):
        url_tokens = ["https://", "ecb.europa.eu"]
        base_url = "https://www.ecb.europa.eu"
        save_path = os.getcwd() + "/data-fed/"
        super().__init__(url_tokens, base_url, save_path)

    def _get_articles_from_list(self, article_list: Tag):
        article_links = [link for link in article_list.find_all("dl")]
        print(article_links)

    def _get_article_list(self, url: str):
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            article_list = soup.find("div", class_="sort-wrapper")
            if article_list:
                return article_list
        else:
            print(f"article_list: No div called article")

    def crawl(self, start_date: datetime, end_date: datetime):
        self._start_date = self._get_month_range(start_date)[0]
        self._end_date = self._get_month_range(end_date)[1]

        current_year = start_date.year
        end_year = end_date.year
        while current_year <= end_year:
            url = (
                self._base_url
                + r"/press/pubbydate/html/index.en.html?topic=Key%20ECB%20interest%20rates&year="
                + str(current_year)
            )
            article_list = self._get_article_list(url)
            articles = self._get_articles_from_list(article_list)
            current_year += 1


ECBCrawler().crawl(datetime(2023, 1, 1), datetime(2024, 3, 31))
