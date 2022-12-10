from configparser import ConfigParser
from argparse import ArgumentParser

from utils.server_registration import get_cache_server
from utils.config import Config  # The config class
from crawler import Crawler


# Requirements
# 1. How many unique pages did you find? Only established by the URL, but discarding the fragment part.
# 2. What is the longest page in terms of the number of words? (HTML markup are not words)
# 3. What are the 50 most common words? (avoid English stop words)
# 4. How many subdomains did you find in the ics.uci.edu domain?

def main(config_file, restart):
    cparser = ConfigParser()
    cparser.read(config_file)

    config = Config(cparser)
    config.cache_server = get_cache_server(config, restart)

    crawler = Crawler(config, restart)
    crawler.start()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--restart", action="store_true", default=False)
    parser.add_argument("--config_file", type=str, default="config.ini")
    args = parser.parse_args()

    main(args.config_file, args.restart)
