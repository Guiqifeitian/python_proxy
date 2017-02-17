#-*- coding:utf-8 -*-
import urllib2
from pymongo import *
import re
import time

class getProxy():
    def __init__(self):
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:51.0) Gecko/20100101 Firefox/51.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        self.dbname="proxydb"

    def getContent(self):
        nn_url = 'http://www.xicidaili.com/nn/'
        req = urllib2.Request(nn_url,headers = self.header)
        res = urllib2.urlopen(req,timeout = 10)
        #print res.read()
        content = res.read()
        print content
        ip = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",content)
        #print ip,len(ip)
        port1 = re.findall(r"<td>\d{2,4}</td>",content)
        port2 = []
        for each in port1:
            port2.append(each[4:-5])
        #print port2,len(port2)
        for i in range(100):
            proxy = {'ip':ip[i],'port':port2[i]}
            print proxy
            if self.isAlive(ip[i],port2[i]):
                self.inser_mongo(proxy)


    #检查代理是否存活
    def isAlive(self,ip,port):
        proxy = {'http':ip+':'+port}
        print proxy

        proxy_support = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)

        test_url = "http://www.ustc.com"

        req = urllib2.Request(test_url, headers=self.header)

        try:
            # timeout 设置为10，如果你不能忍受你的代理延时超过10，就修改timeout的数字
            resp = urllib2.urlopen(req, timeout=10)

            if resp.code == 200:
                print "work"
                return True
            else:
                print "not work"
                return False
        except:
            print "Not work"
            return False

    #可优化
    def inser_mongo(self,proxy):
        client = MongoClient('localhost', 27017)
        db_ = client.proxy
        collection_user = db_['alive']
        collection_user.insert(proxy)
        #collection_user.close()

    #检查数据库中的代理是否存活,删除已经失效的
    def check_db_alive(self):
        client = MongoClient('localhost', 27017)
        db_ = client.proxy
        collection_proxy = db_['alive']
        for eachproxy in collection_proxy.find():
            if not self.isAlive(eachproxy['ip'],eachproxy['port']):
                collection_proxy.remove(eachproxy)

    def loop(self):
        self.getContent()

def main():
    obj = getProxy()
    obj.loop()
    time.sleep(5)
    obj.check_db_alive()

if __name__=='__main__':
    main()
