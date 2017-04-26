# coding:utf-8
import requests
from bs4 import BeautifulSoup
import json
import random
import datetime
import re
import time


class Spiders():
    def __init__(self, all_page=1):
        self.id_ = "thread_list"
        self.key_word = u"毒姐"
        self.key_word_2 = u"情阅"
        self.exclude_1 = u"收"
        self.exclude_2 = u"蹲"
        self.exclude_3 = u"换"
        self.all_page = all_page

    def html_processor(self):
        html_list = []
        for page in xrange(self.all_page):
            pn = page * 50
            thread_urls = "http://tieba.baidu.com/f?kw=%E5%89%91%E7%BD%91%E4%B8%89%E4%BA%A4%E6%98%93&ie=utf-8&pn={0}".format(
                pn)
            s = random.randint(1, 5)
            print page + 1
            time.sleep(s)
            response = requests.get(thread_urls)
            html_list.append(response.content)
        return html_list

    def post_url_processor(self, html):
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
        l = []
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
            time.sleep(random.randint(1, 5))
            u = "{0}?pn={1}".format(post_urls, page)
            print u"第{0}/{1}页".format(page, page_last_num)
            response = requests.get(u)
            soup = BeautifulSoup(response.content, "lxml")
            reply_list = soup.find_all(class_="d_post_content_main ")
            for reply in reply_list:
                tmp = reply.find_all(class_="d_post_content j_d_post_content ")[0]
                tmp2 = reply.find_all('span', class_="tail-info")
                string = u""
                for t in tmp2:
                    string += (t.get_text() + u"#")
                try:
                    d = re.search(r'(\d{4}-\d{2}-\d{2})', string).group(1)
                    d = datetime.datetime.strptime(d, "%Y-%m-%d").date()
                    if d < datetime.date(2017, 4, 18):
                        continue
                except:
                    pass
                for i in tmp.contents:
                    if self.key_word in i and self.key_word_2 in i:
                        if self.exclude_1 in i or self.exclude_2 in i or self.exclude_3 in i:
                            continue
                        try:
                            s = i.get_text()
                        except:
                            s = i.encode("utf-8")
                        s = "{0},{1},{2}".format(s, u, string)
                        l.append(s)
        l = set(l)
        return l


if __name__ == '__main__':
    s = Spiders()
    html_list = s.html_processor()
    page = 0
    with open("/Users/grey/Desktop/tmp.txt", "a") as f:
        for html in html_list:
            page += 1
            post_url_list = s.post_url_processor(html)
            post = 0
            for post_url in post_url_list:
                post += 1
                print u"第{0}页 第{1}个帖子".format(page, post)
                key_list = s.post_processor(post_url)
                for key in key_list:
                    f.write(key.replace(" ", ""))
                    f.write("\n\n")
