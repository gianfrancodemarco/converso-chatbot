import logging
from textwrap import dedent
from typing import Dict, List

import requests
from parsel import Selector
from pydantic import BaseModel, Field

from converso.helpers import HtmlProcessor

logger = logging.getLogger(__name__)


class GoogleSearchClientPayload(BaseModel):
    query: str = Field(
        description="The query to search Google with."
    )
    num_expanded_results: int = Field(
        1,
        description="The number of links to crawl from the result list."
    )


class GoogleSearchClient:
    def __init__(self):
        self.headers = {
            'authority': 'www.google.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9,lt;q=0.8,et;q=0.7,de;q=0.6',
            'cache-control': 'no-cache',
            'dnt': '1',
            'pragma': 'no-cache',
            'sec-ch-ua': '"Not_A Brand";v="99", "Microsoft Edge";v="109", "Chromium";v="109"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-full-version': '"109.0.1518.78"',
            'sec-ch-ua-full-version-list': '"Not_A Brand";v="99.0.0.0", "Microsoft Edge";v="109.0.1518.78", "Chromium";v="109.0.5414.120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"10.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.78',
        }
        self.previous_searches = []

    def search(
        self,
        payload: GoogleSearchClientPayload
    ) -> str:
        if not payload.query:
            raise ValueError("Query cannot be empty")

        logging.info(f"Searching the internet with query: {payload.query}")
        params = {'q': payload.query}

        response = self.make_request(
            'https://www.google.com/search', params=params)

        if response:
            selector = Selector(response.text)
            result = self.parse_search_results(selector, payload=payload)
            self.previous_searches.append(payload.query)
            return result

    def make_request(self, url, params=None):
        params = params or {}
        try:
            response = requests.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.exception(f"Error making request: {e}")

    def parse_search_results(
        self,
        selector: Selector,
        payload: GoogleSearchClientPayload
    ) -> List[Dict[str, str]]:
        # Add parser for other data...

        financial_data = None
        try:
            financial_data = self.__scrape_financial_data(selector)
            logging.info(f"Found financial data: {financial_data}")
        except BaseException as e:
            logging.info(f"No financial data found")

        info_box = None
        try:
            info_box = self._scrape_info_box(selector)
            logging.info(f"Found info box: {info_box}")
        except BaseException as e:
            logger.info(f"No info box found")

        if self._enable_expanded_results(query=payload.query):
            results_list = self._scrape_results_list(selector)
            texts = []
            for result in results_list:
                if len(texts) < payload.num_expanded_results:
                    text = self.get_main_content_from_url(result["url"])
                    if text:
                        texts.append(text)
            if results_list:
                logging.info(f"Found results from websites: {results_list}")
        else:
            texts = []
            logging.info(
                f"First time executing query: {payload.query}, no expanded results")

        if not financial_data and not info_box and not texts:
            raise ValueError(
                "No results found, try again adjusting your query.")

        return dedent(f"""
            {financial_data or ""}
            {info_box or ""}
            {"".join(texts)}
        """)

    def __scrape_financial_data(
            self, selector: Selector) -> List[Dict[str, str]]:
        """
        Scrape financial data from Google search results.
        The first xpath is for "Converter" result type; the second is for "asset chart" result type.
        """

        financial_data = self._get_xpath_with_alternatives(
            selector,
            [
                '//div[@data-attrid="Converter"]',
                '//div[@data-attrid="kc:/finance/stock:asset chart"]'
            ]
        )

        asset_name = self._get_xpath_with_alternatives(
            financial_data,
            [
                '//div[@class="cbXzDb"]//span[2]//text()',
                '//div[@class="oPhL2e"]//span[@data-attrid="Company Name"]//text()'],
            extract_first=True)

        value = self._get_xpath_with_alternatives(
            financial_data,
            [
                '//span[@class="pclqee"]//text()',
                '//span[@jsname="vWLAgc"]//text()'
            ],
            extract_first=True
        )

        currency = self._get_xpath_with_alternatives(
            financial_data,
            [
                '//span[@class="dvZgKd"]//text()',
                '//span[@jsname="T3Us2d"]//text()'
            ],
            extract_first=True
        )

        variation = self._get_xpath_with_alternatives(
            financial_data,
            [
                '//span[@class="iXabQc vgpkr"]',
                '//span[@class="iXabQc ASafz"]',
                '//span[contains(@class, "WlRRw") and contains(@class, "IsqQVc")]'])

        absolute_variation = self._get_xpath_with_alternatives(
            variation,
            [
                '//span[@jsname="SwWl3d"]//text()',
                '//span[@jsname="qRSVye"]//text()'
            ],
            extract_first=True
        )

        percentage_variation = self._get_xpath_with_alternatives(
            variation,
            [
                '//span[@jsname="rfaVEf"]//text()',
                '//span[@class="IsqQVc fw-price-up"]//text()'
            ],
            extract_first=True
        )

        # remove indentation
        return dedent(f"""
            Financial data for {asset_name}:
            Value: {value} {currency}
            Daily variation: {absolute_variation} {currency} {percentage_variation}
        """)

    def _scrape_info_box(self, selector: Selector) -> List[Dict[str, str]]:
        info_box = selector.xpath("//div[@class='I6TXqe']").extract_first()
        if info_box:
            return dedent(f"""
                Found info box:
                {HtmlProcessor.clear_html(info_box)}
            """)

    def _scrape_results_list(self, selector: Selector) -> List[Dict[str, str]]:
        parsed = []
        results = selector.xpath("//div[@id='rso']/*")

        for result in results:
            try:
                result_element = result.xpath(".//a[1]")
                result_url = result_element[0].xpath("@href").extract_first()
                result_title = result_element[0].xpath(
                    ".//h3[1]//text()").extract()

                if result_url != "#":
                    parsed.append({
                        "url": result_url,
                        "title": result_title
                    })
            except IndexError as e:
                logging.exception(f"Error parsing search result: {e}")

        return parsed

    def get_main_content_from_url(
        self,
        url: str
    ):

        try:
            response = self.make_request(url)
        except requests.exceptions.MissingSchema as e:
            logging.info(f"Cannot get content from {url}")

        try:
            if response:
                text_content = HtmlProcessor.clear_html(response.text)
                logging.info(f"Found content from {url}")
                return text_content
        except requests.exceptions.RequestException as e:
            logging.exception(f"Error getting main content from {url}: {e}")

    def _get_xpath_with_alternatives(
        self,
        selector: Selector,
        xpaths: List[str],
        extract_first: bool = False
    ) -> [Selector | str]:
        for xpath in xpaths:
            result = selector.xpath(xpath)
            if result:
                return result.extract_first().strip() if extract_first else result
        return "Not found"

    def _enable_expanded_results(self, query: str) -> bool:
        """
        The first time a query is executed, we try to answer it with quick information (e.g. financial data, info box).
        If the user asks the same question again, we try to answer it with information from websites.
        """
        return True
        return query in self.previous_searches
