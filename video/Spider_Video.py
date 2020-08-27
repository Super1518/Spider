# !usr/bin/env/python
# -*- coding: utf-8 -*-
"""
# version: 1.0
# author : guoxunqiang 
# file   : Spider_Video
# time   : 2020/6/29 22:28
"""
import os
import requests
from bs4 import BeautifulSoup
import ffmpy3
from multiprocessing.dummy import Pool as ThreadPool



class VideoDownloader(object):
    def __init__(self):
        self.server = 'http://www.jisudhw.com/'
        self.search_url = 'http://www.jisudhw.com/index.php?m=vod-search'
        self.search_headers = {
            'UserAgent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            'Host': 'www.jisudhw.com',
            'Origin': 'http://www.jisudhw.com',
            'Referer': 'http://www.jisudhw.com/index.php?m=vod-search'
        }
        search_keyword = '琉璃'

        self.search_parames = {
            'm': 'vod-search'
        }
        self.search_data = {
            'wd': search_keyword,
            'submit': 'search'
        }
        self.video_items = {}
        self.vedio_name = ''

    def _get_video_url(self):
        res = requests.post(url=self.search_url, headers=self.search_headers, params=self.search_parames, data=self.search_data)
        if res.status_code != 200:
            print(res.status_code)
        res.encoding = 'utf-8'
        bf = BeautifulSoup(res.text, 'lxml')
        search_span = bf.find('span', class_='xing_vb4')
        self.vedio_name = search_span.a.string
        if not os.path.exists(self.vedio_name):
            os.mkdir(self.vedio_name)

        video_url = search_span.a.get('href')
        video_url = self.server + video_url
        return video_url

    def _get_video_items(self, url):
        res = requests.get(url)
        if res.status_code != 200:
            print(res.status_code)
            return None
        res.encoding = 'utf-8'
        detail_bf = BeautifulSoup(res.text, 'lxml')
        # li_tag = detail_bf.select("#\31 > ul > li")[0]
        num = 1
        for each_url in detail_bf.find_all('input'):
            if 'm3u8' in each_url.get('value'):
                url = each_url.get('value')
                if url not in self.video_items.keys():
                    self.video_items[url] = num
                    num += 1
        print(self.video_items)

    def _video_download(self, url):
        num = self.video_items[url]
        out_file_path = os.path.join(self.vedio_name, '第%d集.mp4' % num)
        ffmpy3.FFmpeg(inputs={url: None}, outputs={out_file_path: None}).run()

    def dowload(self):
        video_url = self._get_video_url()
        print(video_url)
        self._get_video_items(video_url)
        # for url in self.video_items.keys():
        #     self._video_download(url)
        # 开8个线程池
        pool = ThreadPool(8)
        results = pool.map(self._video_download, self.video_items.keys())
        pool.close()
        pool.join()


if __name__ == '__main__':
    video = VideoDownloader()
    video.dowload()
