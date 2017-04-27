# coding:utf-8

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import datetime
import Levenshtein


class Spiders(object):
    def __init__(self, all_page=1):
        self.id_ = "thread_list"
        self.key_word_list = ()
        self.exclude_word_list = ()
        self.all_page = all_page
        self.result_key_list = []

    def add_key_word(self, *args):
        self.key_word_list += args

    def add_exclude_word(self, *args):
        self.exclude_word_list += args

    def html_processor(self):
        # 处理指定页数的百度剑三交易吧的前x页 并返回其中的html
        html_list = []
        for page in xrange(self.all_page):
            pn = page * 50
            thread_urls = "http://tieba.baidu.com/f?kw=%E5%89%91%E7%BD%91%E4%B8%89%E4%BA%A4%E6%98%93&ie=utf-8&pn={0}".format(
                pn)
            response = requests.get(thread_urls)
            time.sleep(1)
            html_list.append(response.content)
        return html_list

    def post_url_processor(self, html):
        # 处理指定的html 并返回其中所有的post的url
        tmp_list = []
        soup = BeautifulSoup(html, "lxml")
        ul = soup.find_all(id=self.id_)[0]
        l = ul.find_all(class_=" j_thread_list clearfix")
        for i in l:
            post_id = json.loads(i.attrs["data-field"])["id"]
            urls = "https://tieba.baidu.com/p/{0}".format(post_id)
            tmp_list.append(urls)
        return tmp_list

    def post_processor(self, post_urls):
        # 根据post_url 处理一个帖子并返回所有契合关键字的内容
        time.sleep(1)
        if len(self.key_word_list) == 0:
            raise Exception("key_word_list can`t be none")
        result_list = []
        response = requests.get(post_urls)
        soup = BeautifulSoup(response.content, "lxml")
        try:
            tmp_1 = soup.find_all(class_="l_pager pager_theme_5 pb_list_pager")[0]
            page_last_num = tmp_1.find_all("a")[-1].attrs["href"].split("=")[-1]
            page_last_num = int(page_last_num)
        except:
            page_last_num = 1
        for page in xrange(page_last_num):
            page += 1
            post_url_now = "{0}?pn={1}".format(post_urls, page)
            response = requests.get(post_url_now)
            soup = BeautifulSoup(response.content, "lxml")
            reply_list = soup.find_all(class_="d_post_content_main ")
            for reply in reply_list:
                tmp = reply.find_all(class_="d_post_content j_d_post_content ")[0]
                tmp2 = reply.find_all('span', class_="tail-info")
                string = u""
                for t in tmp2:
                    string += t.get_text()
                reply_date = re.search(r'(\d{4}-\d{2}-\d{2})', string).group(1)
                reply_date = datetime.datetime.strptime(reply_date, "%Y-%m-%d").date()
                if reply_date < datetime.date(2017, 4, 15):
                    continue
                for content in tmp.contents:
                    mark = False
                    for key_word in self.key_word_list:
                        if key_word not in content:
                            mark = True
                            break
                    if mark:
                        continue
                    try:
                        reply_content = content.get_text()
                    except:
                        reply_content = content.encode("utf-8")
                    reply_content_key = reply_content.strip()
                    similar_mark = False
                    for result_key in self.result_key_list:
                        if Levenshtein.ratio(reply_content_key, result_key) > 0.9:
                            similar_mark = True
                            break
                    if similar_mark:
                        continue
                    self.result_key_list.append(reply_content_key)
                    reply_content = "{0},{1},{2}".format(reply_content_key, post_url_now, string.encode("utf8"))
                    result_list.append(reply_content)
        return result_list

    def main_processor(self):
        html_list = self.html_processor()
        d = datetime.datetime.now()
        for html in html_list:
            post_url_list = self.post_url_processor(html)
            for post_url in post_url_list:
                result_list = self.post_processor(post_url)

                with open("result_{0}.txt".format(d), "a") as f:
                    for result in result_list:
                        f.write(result.strip())
                        f.write("\n\n")


if __name__ == '__main__':
    start = datetime.datetime.now()
    s = Spiders(all_page=5)
    s.add_key_word(u"情阅", u"毒姐")
    s.add_exclude_word(u"收", u"蹲")
    s.main_processor()
    end = datetime.datetime.now()
    print "start @ {0}".format(start)
    print "end @ {0}".format(end)
    print "all cost {0}".format(end - start)