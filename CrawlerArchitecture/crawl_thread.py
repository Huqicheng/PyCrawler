# -*- coding: utf-8 -*-

import threading
import queue
import urllib.request
import urllib.error
import logging
from bs4 import BeautifulSoup
from bs4.element import ContentMetaAttributeValue
import url_table
import config_load

lock = threading.Lock()
LOG_FILENAME = "log.txt"
logging.basicConfig(filename=LOG_FILENAME, level=logging.NOTSET)


class CrawlClass(threading.Thread):
    """
    Threading the crawler
    """
    def __init__(self, queue, u_table, conf, web_save, web_parse):
        threading.Thread.__init__(self)
        self.queue = queue
        self.u_table = u_table
        self.config = conf
        self.web_save = web_save
        self.web_parse = web_parse

    def run(self):
        """
        open, save and parse the url
        """
        while True:
            # poll a url from the queue
            host = self.queue.get()
            try:
                url = urllib.request.urlopen(host, data=None, timeout=self.config.crawl_timeout)
                # analyze the encoding
                charset = ContentMetaAttributeValue.CHARSET_RE.search(url.headers['content-type'])
                charset = charset and charset.group(3) or None
                response = BeautifulSoup(url.read(), "html.parser", from_encoding=charset)
            except urllib.error.HTTPError as e:
                logging.debug("Exception: %s" % e.code)
                continue
            except urllib.error.URLError as e:
                logging.debug("Exception: %s" % e.reason)
                continue
            except Exception as e:
                logging.debug("Exception: %s" % e)
                continue
            finally:
                # task done
                self.queue.task_done()

            # save the page
            self.web_save.save(host, response, threading.current_thread().getName())

            # parse and get the urls for bfs
            if self.web_parse.cur_depth < self.config.max_depth:
                ans_list = self.web_parse.parse(host, response)
                for ans in ans_list:
                    self.add_url(ans)

    def add_url(self, ans):
        """
        You should check if it's Duplicated in case of recursion.
        """
        if lock.acquire():
            if ans not in self.u_table.all_urls:
                self.u_table.all_urls[ans] = 0
                self.u_table.add_todo_list(ans)
            else:
                logging.debug("Duplicated url: %s" % ans)
            lock.release()
        else:
            logging.debug("Lock error")

if __name__ == '__main__':
    conf = config_load.SpiderConfig()
    conf.load_conf()
    queue = queue.Queue()
    u_table = url_table.UrlTable()

    th = CrawlClass(queue)
    th.u_table = u_table
    th.config = conf
    th.setDaemon(True)
    th.start()

    queue.put(conf.urls[0])
    queue.join()
    print(th.u_table.todo_list)
