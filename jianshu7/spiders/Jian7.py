# -*- coding: utf-8 -*-
import scrapy
import re
import MySQLdb
import json
import codecs
from scrapy.selector import Selector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request,FormRequest
from jianshu7.items import Jianshu7Item
import sys
import random
import time
import string
import logging
import requests
import os

reload(sys)
sys.setdefaultencoding('utf-8')

#本程序抓取简书7日热门，30日热门跟这个一样，网址由http://www.jianshu.com/trending/weekly换成http://www.jianshu.com/trending/monthly
#另外，简述的日报也简单，带上浏览器User-Agent发送Request就可以得到数据，规则：http://www.jianshu.com/u/d9edcb44e2f2?order_by=shared_at&page=页码（瀑布流加载）
class Jian7Spider(scrapy.Spider):
    name = "Jian7"
    allowed_domains = ["jianshu.com"]
    start_urls = ['http://www.jianshu.com/trending/weekly']
    ids = []
    ans = 2
    header = {
        "Accept": "text/html, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Cookie":"_session_id=SUwxRnh3WVM4MUt3ekJyNkplNU8wRFlqNkRocmRUcXptZ3BNNG5RY0IvT2o0M1NaZXVRSHBXQmxmb3pRb1NlVE9M\
ci9pQ1YySDl6K3hOa3lOMDVkK1dDeDhnVHZaWmUzanNrUWJKMEZaVk1sN2U3THFtT01XOXdvNEwyOUtNTDZyWmNzN1hTUkxZSHJv\
RmNzb1JZK0ZkTW9jbzJ1RGhuYnlHbkNsSGsycDhDWVJXeHJhcmp5QWNvYUcrUDY1NXZtNWlubllLb0hIc01JMUFBeVBLTitSNGtG\
Zm9jUmtEQm1kZ3hyQW5neFJsMHpGaXVrcU9EMTZNQ3ljMXhxQkVtQkU5dU8yVlZQK2RYRFRxUUhENFpxZkw0VXU1Mk42WVk5RWo2\
czBnRldkd0dIZWdKVkFRNFFWclUzNkRRbmFQalNHQ01LendkS2dwdzd4cHZMYmJPdHlIV2wwbUhYVlcyL2t5ZWFOSTlqNXgyUzlM\
U0FmbFV2SjBWZHowVElUTXZiQndvd05FWXJUTFo0NFJUWlhpZEpTRERkbVdKcU5pSE45VksvTnhBdjVlYz0tLTFGQlhIYU9obGtKMkMvUEpjdU9paUE9PQ\
%3D%3D--70c0d5dfc7cf8945ccf7859d167d6f84f185348b",
        "Host": "www.jianshu.com",
        "Referer": "http://www.jianshu.com/trending/weekly?utm_medium=index-banner-s&utm_source=desktop",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "X-CSRF-Token": "roAZq+By6e1hnnwyDtlfWHU6zgEX8UFMkxmKmK2cU1Nz50fP3YXFYo5RnbAG/aQlu3/497r9PPFEDyxUre+nWg==",
        "X-INFINITESCROLL": "true",
        "X-Requested-With": "XMLHttpRequest"
    }


    def parse(self, response):
        sel = Selector(response)
        lis = sel.xpath('/html/body/div/div/div[1]/div/ul/li')
        for x in lis:
            data_id = x.xpath('@data-note-id').extract()[0]
            self.ids.append(data_id)
            p_id = x.xpath('div/a').xpath('@href').extract()[0]
            yield Request('http://www.jianshu.com'+p_id,meta={"p_id":p_id},callback=self.parse_item)

        sum1 = '&seen_snote_ids[]='.join(self.ids)
        url = 'http://www.jianshu.com/trending/weekly?seen_snote_ids[]='+sum1+'&page='+str(2)
        # print url
        yield Request(url,meta={'url':url},headers=self.header,callback=self.page_two)



    def page_two(self,response):
        last_url = response.meta['url']
        new_url = re.sub('&page=\d',"",last_url)
        self.ans += 1

        sel = Selector(response)
        lis = sel.xpath('//li')
        id = []
        for x in lis:
            data_id = x.xpath('@data-note-id').extract()[0]
            # print data_id
            new_url = new_url + '&seen_snote_ids[]=' + str(data_id)
            p_id = x.xpath('div/a').xpath('@href').extract()[0]
            yield Request('http://www.jianshu.com' + p_id, meta={"p_id": p_id}, callback=self.parse_item)
        new_url = new_url + '&page=' + str(self.ans)
        print 'new_urll:', new_url
        yield Request(new_url, meta={'url': new_url}, headers=self.header, callback=self.page_two)
        # if self.ans >= 15:
        #     sys.exit()


    #爬每篇文章内容
    def parse_item(self,response):
        sele = Selector(response)
        item = Jianshu7Item()
        try:
            item['auther'] = sele.xpath('/html/body/div[1]/div[1]/div[1]/div[1]/div/span[2]/a/text()').extract()[0]
        except:
            item['auther'] = ""
        try:
            item['article_name'] = sele.xpath('/html/body/div[1]/div[1]/div[1]/h1/text()').extract()[0]
        except:
            item['article_name'] = ""
        content = sele.xpath('/html/body/div[1]/div[1]/div[1]/div[2]').extract()[0]
        content = re.sub('</\w*>', '\n', content)
        content = re.sub('<[^>]+>','',content)
        content.replace("图片发自简书App","")
        content.replace("\n","")
        item['content'] = content
        item['link'] = 'http://www.jianshu.com'+ response.meta['p_id']
        return  item



