from threading import Thread
from utils.tokenizer import Tokenizer
from inspect import getsource
from utils.download import download
from utils import get_logger, get_no_seg_urlhash, normalize
import scraper
from scraper import is_valid
from scraper import check_content_type
import time
from bs4 import BeautifulSoup


# .logger : logs messages from Worker class
# .config : object of class Config
# .frontier : object of class Frontier


class Worker(Thread):  # A worker is a subclass of Thread
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "WORKER")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {
            -1}, "Do not use requests from scraper.py"
        super().__init__(daemon=True)

    def run(self):

        freq_dict = dict();

        while True:
            # Get a URL from frontier
            tbd_url = self.frontier.get_tbd_url()

            # Check if there are still URLs left
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            # Check if this URL is valid
            # if not scraper.is_valid(tbd_url):
            # self.logger.info(f"{tbd_url} is not valid!")
            # continue

            resp = download(tbd_url, self.config, self.logger)

            if is_valid(tbd_url):

                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")

                # Get a list of scrapped URLs
                scraped_urls = scraper.scraper(tbd_url, resp)

                # Add scraped URLs to frontier
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)

                # Mark the current URL as complete
                self.frontier.mark_url_complete(tbd_url)

                # Delay for politeness
                time.sleep(self.config.time_delay)

                # The actual content processing happens here
                if resp.status == 200 and is_valid(resp.raw_response.url) and check_content_type(resp, self.logger):

                    # Analyze the page content here ...

                    soup = scraper.get_soup(resp)

                    raw_content = soup.get_text()

                    # print(raw_content)

                    # Save the unique page
                    url = normalize(resp.url)  # remove the '/' at the end of the url, if there's one
                    no_seg_urlhash = get_no_seg_urlhash(url)  # generate hash, not include scheme

                    if no_seg_urlhash not in self.frontier.unique_page_save:
                        tokens_list = Tokenizer.tokenize(raw_content)

                        word_count = len(tokens_list)  # is for requirement 2
                        freq_dict = Tokenizer.compute_word_frequencies(tokens_list, freq_dict)

                        # use tokenizer compute word freq (source = word_count filtered = discard the stop words)

                        self.frontier.unique_page_save[no_seg_urlhash] = (url, word_count)  # hash : (url, word_count)
                        self.frontier.unique_page_save.sync()  # save

                elif 201 <= resp.status <= 599:
                    # status code is between 201-599
                    self.logger.error(
                        'STATUS CODE: ' + str(resp.status) + '; REQUEST URL: ' + tbd_url + '; RESPONSE URL: ' + str(
                            resp.url))

                elif 600 <= resp.status:
                    # status code is >= 600
                    self.logger.error(
                        'STATUS CODE: ' + str(resp.status) + '; REQUEST URL: ' + tbd_url + '; RESPONSE URL: ' + str(
                            resp.url) + '; MESSAGE: ' + resp.error)

        # The crawler has crawled everything! Time for stats
        self.frontier.logger.info("===== END REPORT =====")
        self.frontier.logger.info(f"Found {len(self.frontier.all_url_save)} total urls.")
        self.frontier.process_unique_page()
        self.frontier.process_unique_subdomain()
        Tokenizer.print_map(freq_dict)
