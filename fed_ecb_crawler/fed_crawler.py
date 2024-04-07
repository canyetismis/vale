from fed_ecb_crawler.crawler_base import CrawlerBase, ArticleModel
import requests
from bs4 import BeautifulSoup, Tag
import re
import os

# import requests
from datetime import datetime


class FEDCrawler(CrawlerBase):
    def __init__(self):
        url_tokens = ["https://", "federalreserve.gov"]
        base_url = "https://www.federalreserve.gov"
        save_path = os.getcwd() + "/data-fed/"
        super().__init__(url_tokens, base_url, save_path)

    def _parse_a_b(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            title = soup.find("h3", class_="title")
            title = title.text.strip()
            link = url

            content = soup.find("div", class_="col-xs-12 col-sm-8 col-md-8")
            if content:
                content = "\n".join(
                    [
                        p.get_text(strip=True)
                        for p in content.find_all("p", class_=False)
                    ]
                )

            pubDate = datetime.strptime(
                soup.find("p", class_="article__time").text.strip(), "%B %d, %Y"
            )
            source_id = "fed"
            source_url = self._base_url
            country = ["united states of america"]

            model = ArticleModel(
                title=title,
                link=link,
                content=content,
                pubDate=pubDate,
                source_id=source_id,
                source_url=source_url,
                country=country,
            )

            return model
        else:
            print(f"Failed to fetch {url}")

    def _parse_a1(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            heading_divs = soup.find("div", class_="heading col-xs-12")
            title = heading_divs.find("h3").text.strip()
            link = url

            content_rows = soup.find_all("div", class_="row")

            for row in content_rows:
                div_col = row.find("div", class_="col-xs-12")
                if div_col and "heading" not in div_col["class"]:
                    content = div_col.get_text()
                    break

            pubDate = datetime.strptime(
                soup.find("p", class_="article__time").text.strip(), "%B %d, %Y"
            )
            source_id = "fed"
            source_url = self._base_url
            country = ["united states of america"]

            model = ArticleModel(
                title=title,
                link=link,
                content=content,
                pubDate=pubDate,
                source_id=source_id,
                source_url=source_url,
                country=country,
            )

            return model
        else:
            print(f"Failed to fetch {url}")

    def _check_url_date(self, url: str):
        match = re.search(r"(\d{8})", url)
        if match:
            datetime_str = match.group(1)
            return self._check_date(
                datetime.strptime(datetime_str, "%Y%m%d"),
                self._start_date,
                self._end_date,
            )

    def _get_articles_from_list(self, article_list: Tag):
        article_list_div = article_list.find_all("div", class_="fomc-meeting")

        articles = []
        for article in article_list_div:
            article_links = [
                self._base_url + link.get("href")
                for link in article.find_all("a")
                if (
                    re.search(r"monetary\d+a1\.htm", link.get("href"))
                    or re.search(r"monetary\d+a\.htm", link.get("href"))
                    or re.search(r"monetary\d+b\.htm", link.get("href"))
                )
                and self._check_url_date(link.get("href"))
            ]

            for link in article_links:
                if re.search(r"monetary\d+a1\.htm", link):
                    articles.append(self._parse_a1(link))
                else:
                    articles.append(self._parse_a_b(link))
        return articles

    def _get_article_list(self):
        url = f"{self._base_url}/monetarypolicy/fomccalendars.htm"
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            article_list = soup.find("div", id="article")
            if article_list:
                return article_list
            else:
                print(f"article_list: No div called article")

        else:
            print(f"Failed to fetch {url}")

    def crawl(self, start_date: datetime, end_date: datetime):
        self._start_date = self._get_month_range(start_date)[0]
        self._end_date = self._get_month_range(end_date)[1]

        article_list = self._get_article_list()
        articles = self._get_articles_from_list(article_list)
        articles = self._group_articles(articles)
        self._save(articles)


FEDCrawler().crawl(datetime(2023, 1, 1), datetime(2024, 3, 31))
