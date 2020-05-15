import requests
import pymysql
import time
from random import choice
from bs4 import BeautifulSoup

REQUEST_QUEUE = []
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
                         '/81.0.4044.92 Safari/537.36'}
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'zblog'
MYSQL_PORT = 3306
MYSQL_USER = 'zblog'
MYSQL_PASSWORD = '123456'
PROCESS_STATE = {
    'free': 0,
    'work': 1,
    'finish': 2,
}
SESSION = requests.session()
DELAY_TIME = 0.5
TABLE_NAME = 'zbp_post'
CLICK_RANGE = [x for x in range(100)]

START_URL = 'https://www.cnblogs.com/cate/dotnetcore/'


class Storage:
    def __init__(self):
        self.host = MYSQL_HOST
        self.database = MYSQL_DATABASE
        self.user = MYSQL_USER
        self.password = MYSQL_PASSWORD
        self.port = MYSQL_PORT
        self.db = None
        self.cursor = None

    def open(self):
        self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                                  port=self.port)
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def save(self, item):
        keys = ', '.join(item.keys())
        values = ', '.join(['%s'] * len(item))
        sql = 'insert into %s (%s) values (%s)' % (TABLE_NAME, keys, values)
        self.cursor.execute(sql, tuple(item.values()))
        self.db.commit()


class Request:
    def __init__(self, url: str, onfinish=None):
        self.url = url
        self.finished = False
        self.processing = False
        self.onfinish = onfinish

    def finish(self, response: requests.Response):
        self.finished = True
        if self.onfinish is not None:
            self.onfinish(response)


STORAGE = Storage()
finish_count = 0


def crawl_page(response: requests.Response):
    bs = BeautifulSoup(response.text, 'lxml')
    url_items = bs.find_all(name='a', attrs={'class': 'titlelnk'})
    for i in url_items:
        REQUEST_QUEUE.insert(len(REQUEST_QUEUE) - finish_count, Request(i['href'], crawl_article))
    last_page = bs.find(attrs={'class': 'pager'}).find_all(name='a').pop()
    if 'Next' in last_page.string:
        REQUEST_QUEUE.insert(len(REQUEST_QUEUE) - finish_count, Request(f'https://www.cnblogs.com{last_page["href"]}', crawl_page))


def crawl_article(response: requests.Response):
    bs = BeautifulSoup(response.text, 'lxml')
    title_tag = bs.find(name='a', attrs={'class': 'postTitle2'})
    body_tag = bs.find(name='div', attrs={'id': 'cnblogs_post_body'})
    if title_tag is None or body_tag is None:
        return
    print(title_tag.string)
    entity = dict()
    entity['log_CateID'] = 2
    entity['log_AuthorID'] = 1
    entity['log_Tag'] = ''
    entity['log_Status'] = 0
    entity['log_Type'] = 0
    entity['log_Alias'] = title_tag.string
    entity['log_IsTop'] = 0
    entity['log_IsLock'] = 0
    entity['log_Title'] = title_tag.string
    entity['log_Intro'] = f'{body_tag.text[0: 100]}<!--autointro-->'
    entity['log_Content'] = str(body_tag)
    time_tag = bs.find(name='span', attrs={'id': 'post-date'})
    time_array = time.strptime(time_tag.string, '%Y-%m-%d %H:%M')
    entity['log_PostTime'] = int(time.mktime(time_array))
    entity['log_CommNums'] = 0
    entity['log_ViewNums'] = choice(CLICK_RANGE)
    entity['log_Template'] = ''
    entity['log_Meta'] = ''
    STORAGE.save(entity)


def process_request(req: Request):
    response = SESSION.get(req.url, headers=HEADERS)
    req.finish(response)


def run():
    print('程序运行...')
    STORAGE.open()
    state = PROCESS_STATE['free']
    global finish_count

    REQUEST_QUEUE.append(Request(START_URL, crawl_page))

    while True:
        time.sleep(DELAY_TIME)
        if state == PROCESS_STATE['free']:
            if len(REQUEST_QUEUE) <= 0 or len(REQUEST_QUEUE) == finish_count:
                continue
            process_request(REQUEST_QUEUE[0])
            state = PROCESS_STATE['work']
        if state == PROCESS_STATE['work'] and REQUEST_QUEUE[0].finished:
            finish_count = finish_count + 1
            state = PROCESS_STATE['finish']
            print(f'# finish_count: {finish_count}, processed url is {REQUEST_QUEUE[0].url}')
        if state == PROCESS_STATE['finish']:
            item = REQUEST_QUEUE.pop(0)
            REQUEST_QUEUE.append(item)
            state = PROCESS_STATE['free']


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        STORAGE.close()
        print('程序终止...')
