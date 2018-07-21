#!/usr/bin/python
# -*- coding: UTF-8 -*-
import io,sys,re,os,json
import requests
from requests.exceptions import RequestException
from multiprocessing import Pool

#修改编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')

def write_to_file(content):
    '''
    将文本信息写入文件
    '''
    with open('result.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')
        f.close()

def save_image_file(url, path):
    '''
    保存电影封面
    '''
    ir = requests.get(url)
    if ir.status_code == 200:
        with open(path, 'wb') as f:
            f.write(ir.content)
            f.close()

def get_one_page(url):
    """获取网页HTML内容并返回"""
    try:
        #获取网页HTML内容
        response = requests.get(url)
        #通过状态码判断是否获取成功
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_one_page(html):
    """解析HTML代码，提取有用信息并返回"""
    # 正则表达式进行解析
    pattern = re.compile('<tr class="item">.*?title="(.*?)"'+
        '.*?<img src="(.*?)"'+'.*?(\d{4}-\d{2}-\d{2}.*?\))'+
        '.*?/(.*?)/(.*?)/(.*?)/(.*?)/'+
        '.*?rating_nums">(.*?)</span>.*?</tr>',re.S)
    # 匹配所有符合条件的内容
    items = re.findall(pattern,html)

    for item in items:
        yield {
            'title': item[0],
            'image': item[1],
            'time': item[2].strip(),
            'actor': item[5:6],
            'score': item[7]
        }

def main(offset):
    #豆瓣电影
    url = 'https://movie.douban.com/chart'+str(offset)
    html = get_one_page(url)

   # 封面文件夹不存在则创建
    if not os.path.exists('covers'):
        os.mkdir('covers')

    for item in parse_one_page(html):
        print(item)
        write_to_file(item)
        save_image_file(item['image'], 'covers/' + item['title'] + '.jpg')


if __name__ == '__main__':
    #多线程
    pool = Pool()
    pool.map(main, [i*10 for i in range(10)])