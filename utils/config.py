import re


# .user_agent : string
# .thread_count : int
# .save_file : string
# .host : string
# .port : int
# .seed_url : a list of string
# .time_delay (politeness) : int
# .cache_server (init to None) : tuple(string, int) the cache_server address styx.ics.uci.edu and the port

class Config(object):
    def __init__(self, config):
        self.user_agent = config["IDENTIFICATION"]["USERAGENT"].strip()
        print(self.user_agent)  # This is the line that prints the user agent in the console
        assert self.user_agent != "DEFAULT AGENT", "Set useragent in config.ini"
        assert re.match(r"^[a-zA-Z0-9_ ,]+$",
                        self.user_agent), "User agent should not have any special characters outside '_', ',' and 'space'"
        self.threads_count = int(config["LOCAL PROPERTIES"]["THREADCOUNT"])

        self.all_url_save = config["LOCAL PROPERTIES"]["SAVE"]
        self.unique_page_save = config["LOCAL PROPERTIES"]["SAVE2"]

        self.host = config["CONNECTION"]["HOST"]
        self.port = int(config["CONNECTION"]["PORT"])

        self.seed_urls = config["CRAWLER"]["SEEDURL"].split(",")
        self.time_delay = float(config["CRAWLER"]["POLITENESS"])

        self.cache_server = None
