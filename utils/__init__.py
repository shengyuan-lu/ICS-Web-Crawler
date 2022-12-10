import os
import logging
from hashlib import sha256
from urllib.parse import urlparse


def get_logger(name, filename=None):
    '''Get a logger to log events during crawling'''
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not os.path.exists("Logs"):
        os.makedirs("Logs")
    fh = logging.FileHandler(f"Logs/{filename if filename else name}.log")
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_no_scheme_urlhash(url):
    '''Get the hashvalue of the url'''
    parsed = urlparse(url)
    # Hash everything other than scheme.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}/{parsed.fragment}".encode("utf-8")).hexdigest()


def get_no_seg_urlhash(url):
    parsed = urlparse(url)
    # Hash everything other than scheme and segment.
    return sha256(
        f"{parsed.netloc}/{parsed.path}/{parsed.params}/"
        f"{parsed.query}".encode("utf-8")).hexdigest()


def normalize(url):
    '''Remove the / at the end of url if there is one'''
    if url.endswith("/"):
        return url.rstrip("/")
    return url
