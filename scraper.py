import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# This is where the crawling happens
def extract_next_links(url, resp):
    """Extract links from the response"""
    # Doesn't have to check if link is valid

    next_links = list()

    # url: the URL that was used to get the page
    # print('url: ' + url)

    # resp.url: the actual URL of the page (in case of redirect)
    # print('resp.url: ' + resp.url)

    # resp.status: the status code returned by the server. 200 is OK
    # Other numbers mean that there was some kind of problem.

    if resp.status == 200 and is_valid(url) and is_valid(resp.raw_response.url):
        # status code is 200 OK, so parse the page here:

        # resp.raw_response: this is where the page actually is.
        #         resp.raw_response.url: the url (with / at the end, not normalized)
        #         resp.raw_response.content: the content of the page

        soup = get_soup(resp)

        # How to extract url from page content
        a_tags = soup.find_all('a')

        for tag in a_tags:
            link = tag.get('href', None)
            if link is not None:
                next_links.append(link)

    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    return next_links


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def get_soup(resp):
    if resp.status == 200:
        content = resp.raw_response.content  # the html content
        # print(content)
        return BeautifulSoup(content, features='html.parser')

    else:
        return None


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.

    allowed_scheme_set = {'http', 'https'}
    black_list = {'http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018',
                  'http://www.informatics.uci.edu/files/pdf/InformaticsBrochure-March2018/',
                  'http://www.ics.uci.edu/~shantas/publications/20-secret-sharing-aggregation-TKDE-shantanu'}

    # Debug
    # return False

    parsed = urlparse(url)

    try:
        if url in black_list:
            return False

        elif parsed.scheme not in allowed_scheme_set:
            return False

        elif url.lower().endswith('.pdf'):
            return False

        elif not is_valid_host_name(parsed):
            return False

        elif not is_valid_path(parsed):
            return False

        elif not is_valid_query(parsed):
            return False

        return True

    except TypeError:
        print('TypeError for ', parsed)
        raise


def is_valid_host_name(parsed):
    allowed_hostname_set = {'www.ics.uci.edu', 'www.cs.uci.edu', 'www.informatics.uci.edu', 'www.stat.uci.edu'}

    if parsed.hostname:

        hostname = parsed.hostname

        if hostname == 'www.today.uci.edu':
            if parsed.path.startswith('/department/information_computer_sciences'):
                return True
            else:
                return False

        elif hostname in allowed_hostname_set:
            return True

        elif hostname.endswith('.ics.uci.edu') or hostname.endswith('.cs.uci.edu') or hostname.endswith(
                '.informatics.uci.edu') or hostname.endswith('.stat.uci.edu'):
            return True

        else:
            return False

    else:
        return False


def is_valid_path(parsed):
    not_allowed_file_set = {'css', 'js', 'bmp', 'gif', 'jpg', 'jpeg', 'ico',
                            'png', 'tif', 'tiff', 'mid', 'mp2', 'mp3', 'mp4',
                            'wav', 'avi', 'mov', 'mpeg', 'ram', 'm4v', 'mkv', 'ogg', 'ogv', 'pdf', 'ps', 'eps', 'tex',
                            'ppt', 'pptx', 'ppsx', 'doc', 'docx', 'xls', 'xlsx', 'names',
                            'data', 'dat', 'exe', 'bz2', 'tar', 'msi', 'bin', '7z',
                            'psd', 'dmg', 'iso', 'epub', 'dll', 'cnf', 'tgz', 'sha1', 'thmx', 'mso', 'arff', 'rtf',
                            'jar', 'csv', 'rm', 'smil', 'wmv', 'swf', 'wma', 'zip', 'rar', 'gz'}
    if re.match(
            r'.*\.(css|js|bmp|gif|jpe?g|ico'
            + r'|png|tiff?|mid|mp2|mp3|mp4'
            + r'|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf'
            + r'|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names'
            + r'|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso'
            + r'|epub|dll|cnf|tgz|sha1'
            + r'|thmx|mso|arff|rtf|jar|csv'
            + r'|rm|smil|wmv|swf|wma|zip|rar|gz)$', parsed.path.lower()):
        return False

    lower_cap_path = parsed.path.lower()

    for string in lower_cap_path.strip('/').split('/'):
        if string in not_allowed_file_set:
            return False
        else:
            return True


def is_valid_query(parsed):
    queries = parsed.query.strip('&').split('&')

    for q in queries:
        if re.match(
                r'.*\.(css|js|bmp|gif|jpe?g|ico'
                + r'|png|tiff?|mid|mp2|mp3|mp4'
                + r'|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf'
                + r'|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names'
                + r'|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso'
                + r'|epub|dll|cnf|tgz|sha1'
                + r'|thmx|mso|arff|rtf|jar|csv'
                + r'|rm|smil|wmv|swf|wma|zip|rar|gz)$', q):
            return False

    return True


def check_content_type(resp, logger):
    # banned_content_type = {'application/pdf', 'application/pdf;charset=UTF-8', 'application/pdf; charset=UTF-8'}

    # allowed_content_type = {'text/html; charset=utf-8'}

    if resp.content_type.startswith('text/'):
        return True

    else:
        logger.error(resp.url + 'has content type ' + resp.content_type)
        return False
