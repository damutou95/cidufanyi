import redis
import requests
import pymysql
import re
from lxml import etree
import hashlib
import random
import logging
import pymongo
import time
from pymongo.errors import  DuplicateKeyError


def getDetails(selector):
    sens = selector.xpath('//div[@class="sen2"]')
    for sen in sens:
        if 'createPlayer' in sen.xpath('string(.//div[@class="en_sen2"])'):
            enSen = re.sub('<.*?>', '', re.findall('createPlayer\(\d+,\'(.*?)\'\);', sen.xpath('string(.//div[@class="en_sen2"])'))[0]).replace('\\', '')
        else:
            enSen = sen.xpath('string(.//div[@class="en_sen2"])').strip().replace('\n', '')
        cnSen = sen.xpath('string(.//div[@class="cn_sen2"])')
        yield {'enSen': enSen, 'cnSen': cnSen }

def getProxies():
    proxy = pymysql.Connect(host='127.0.0.1', user='root', password='18351962092', db='proxies')
    cursor = proxy.cursor()
    sql = 'select * from proxy limit 0,20'
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    proxy.close()
    proxies = []
    for row in results:
        ip = row[0]
        port = row[1]
        proxy = f'http://{ip}:{port}'
        proxies.append(proxy)
    proxy = random.choice(proxies)
    return {'https': proxy, 'http': proxy}

def saveTomongo(content):
    client = pymongo.MongoClient(host='127.0.0.1', port=27017)
    db = client['cidufanyi']
    col = db['fanyi']
    sentence = content['enSen'] + content['cnSen']
    hash = hashlib.md5()
    hash.update(sentence.encode('utf-8'))
    hashCode = hash.hexdigest()
    data = {'_id': hashCode, 'enSen': content['enSen'], 'cnSen': content['cnSen'], 'time': time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())}
    col.insert(data)


if __name__ == '__main__':
    enDb = pymysql.Connect(host='127.0.0.1', user='root', password='18351962092', db='frequentwords')
    cursor2 = enDb.cursor()
    sql2 = 'select * from zh_full limit 0,50000'
    cursor2.execute(sql2)
    results2 = cursor2.fetchall()
    url = 'http://www.dictall.com/dictall/result_sentence.jsp'
    for i in results2:
        word = i[0]
        with open('saved.txt', 'r') as f:
            saved = [x.strip('\n') for x in f.readlines()]
        if word not in saved:
            form = {
                'cd': 'UTF-8',
                'keyword': word
                }
            #若代理失效，重新发请求，重新获取代理，最多五次
            for i in range(5):
                html = requests.post(url, data=form) #proxies=getProxies())
                if html.status_code == 200:
                    with open('saved.txt', 'a') as f:
                        f.write(word + '\n')
                    break
            selector = etree.HTML(html.text)
            for i in getDetails(selector):
                try:
                    saveTomongo(i)
                except DuplicateKeyError:
                    continue
                logging.info('#'*20 + '成功写入数据！')




