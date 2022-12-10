import os
import shelve
from utils import get_logger, get_no_scheme_urlhash, normalize
from urllib.parse import urlparse
from scraper import is_valid  # the is_valid function that determines if an url is valid
from threading import Thread, RLock
from queue import Queue, Empty


# .logger : a logger to record Frontier class activities
# .config : object of class Config
# .to_be_downloaded : list of urls to be crawled

class Frontier(object):  # Frontier is a subclass of object
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")  # Get a logger named "FRONTIER"
        self.config = config  # The config object from Config class
        self.to_be_downloaded = list()  # Add urls to be crawled

        if not os.path.exists(self.config.all_url_save) and not restart:  # save file doesn't exist, and restart = False
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.all_url_save}, "
                f"starting from seed.")

            # Remove unique url save if there's one
            if os.path.exists(self.config.unique_page_save):
                self.logger.info(
                    f"Found save file {self.config.unique_page_save}, deleting it.")
                os.remove(self.config.unique_page_save)

        elif os.path.exists(self.config.all_url_save) and restart:  # save file exist, and restart = True
            # Save file does exist, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.all_url_save}, deleting it.")

            os.remove(self.config.all_url_save)

            # Remove unique url save if there's one
            if os.path.exists(self.config.unique_page_save):
                self.logger.info(
                    f"Found save file {self.config.unique_page_save}, deleting it.")
                os.remove(self.config.unique_page_save)

        # Load existing save file, or create one if it does not exist.
        self.all_url_save = shelve.open(self.config.all_url_save)  # hash : (url, is_crawled)
        self.unique_page_save = shelve.open(self.config.unique_page_save)  # hash : (url, word_count)

        # restart from the seed urls
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        # resume last time, set the frontier state with contents of save file.
        else:
            self._parse_save_file()
            if not self.all_url_save:
                for url in self.config.seed_urls:
                    self.add_url(url)

    def _parse_save_file(self):
        """ This function can be overridden for alternate saving techniques. """
        total_count = len(self.all_url_save)
        tbd_count = 0  # the amount of url that is discovered but not crawled
        for url, completed in self.all_url_save.values():  # looks like self.save.value() returns a tuple(str, bool)
            if not completed and is_valid(url):  # url not completed and valid
                self.to_be_downloaded.append(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")  # log

        # Process unique page
        self.process_unique_page()

    def process_unique_page(self):
        unique_pages_count = len(self.unique_page_save)

        self.logger.info(
            f"Found {unique_pages_count} total unique pages.")

        if unique_pages_count > 0:
            max_word_count = 0
            max_wc_url = ""

            for url, word_count in self.unique_page_save.values():

                if word_count > max_word_count:
                    max_word_count = word_count
                    max_wc_url = url

            self.logger.info(
                f"Current max word count: {max_word_count} from url {max_wc_url}")

    def get_tbd_url(self):
        """Get an url that is not crawled yet"""
        try:
            # Get the last element of self.to_be_downloaded
            return self.to_be_downloaded.pop()
        except IndexError:
            return None

    def add_url(self, url):
        """Add a normalized url that is not crawed yet"""
        url = normalize(url)  # remove the '/' at the end of the url, if there's one
        no_scheme_urlhash = get_no_scheme_urlhash(url)  # generate hash, not include scheme

        if no_scheme_urlhash not in self.all_url_save:
            self.all_url_save[no_scheme_urlhash] = (url, False)  # key = no_scheme_urlhash, value = (url, isScrapped)
            self.all_url_save.sync()  # save
            self.to_be_downloaded.append(url)  # Add url to be crawed, because it is newly discovered

    def mark_url_complete(self, url):
        """Mark the url as successfully crawled"""
        urlhash = get_no_scheme_urlhash(url)  # calculate key

        if urlhash not in self.all_url_save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.all_url_save[urlhash] = (url, True)  # Mark URL as already crawed
        self.all_url_save.sync()  # save

    def process_unique_subdomain(self):

        dic = dict()

        for url, _ in self.unique_page_save.values():

            parsed = urlparse(url)

            host_name = parsed.hostname

            if host_name.startswith('www.'):
                host_name = host_name.strip('www.')

            if host_name.endswith('.ics.uci.edu'):
                if host_name in dic.keys():
                    dic[host_name] += 1
                else:
                    dic[host_name] = 1

        # Log from dic
        self.logger.info('=== UNIQUE PAGES OF SUBDOMAINS ===')

        for key in sorted(dic.keys()):
            self.logger.info(key + ', ' + str(dic[key]))
