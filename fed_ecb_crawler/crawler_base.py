from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Tuple, Union, Dict
from datetime import datetime, timedelta
from bs4 import Tag
from collections import defaultdict
import json


class ArticleModel(BaseModel):
    # newsdata syntax
    article_id: None = None
    title: str
    link: str
    keywords: None = None
    creator: None = None
    video_url: None = None
    description: None = None
    content: str
    pubDate: datetime
    image_url: None = None
    source_id: str
    source_url: str
    source_icon: None = None
    source_priority: int = 1
    country: List[str]
    category: None = None
    language: str = "english"
    ait_tag: None = None
    ai_region: None = None
    sentiment: None = None
    sentiment_stats: None = None

    def dict(self, **kwargs):
        # Call the parent class's dict method
        base_dict = super().dict(**kwargs)

        # Convert pubDate to the desired format
        base_dict["pubDate"] = self.pubDate.strftime("%Y-%m-%d %H:%M:%S")

        return base_dict


class CrawlerBase(ABC):
    def __init__(self, url_tokens: List[str], base_url: str, save_path: str) -> None:
        self._url_tokens = url_tokens
        self._base_url = self._check_url(base_url)
        self._save_path = save_path
        self._start_date = None
        self._end_date = None

    def _check_url(self, url: str) -> Union[str, None]:
        if not self._url_tokens:
            raise ValueError("URL tokens needed to run")

        if not url:
            return None

        _pass = all(url_token in url for url_token in self._url_tokens)
        if not _pass:
            return None

        return url

    def _check_date(
        self, date: datetime, start_date: datetime, end_date: datetime
    ) -> bool:
        return start_date <= date <= end_date

    def _get_month_range(self, date: datetime) -> Tuple[datetime, datetime]:
        # Calculate the first day of the month
        first_day_of_month = date.replace(day=1)

        # Calculate the last day of the month
        next_month = first_day_of_month.replace(day=28) + timedelta(days=4)
        last_day_of_month = next_month - timedelta(days=next_month.day)

        return first_day_of_month, last_day_of_month

    def _group_articles(self, articles: List[ArticleModel]):
        grouped_articles = defaultdict(list)

        for article in articles:
            start_date, end_date = self._get_month_range(article.pubDate)
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            key = f"{start_date}_{end_date}"
            grouped_articles[key].append(article)

        return grouped_articles

    def _save(self, articles: Dict[str, List[ArticleModel]]):
        for date_range, article_group in articles.items():
            data = {"articles": [article.dict() for article in article_group]}
            with open(f"{self._save_path}{date_range}.json", "w") as json_file:
                json.dump(data, json_file, indent="\t", ensure_ascii=True)

    @abstractmethod
    def _get_articles_from_list(self, article_list: Tag):
        pass

    @abstractmethod
    def _get_article_list(self, url: str):
        pass

    @abstractmethod
    def crawl(self):
        pass
