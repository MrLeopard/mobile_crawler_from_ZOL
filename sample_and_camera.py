# -*- coding: UTF-8 -*-
import random
import re
import sys
from urllib2 import Request, urlopen

import xlwt
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

urls = {
    "2019": u'http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s8010_1_1_0_1.html',
    "2018": u"http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s7500_1_1_0_1.html",
    "2017": u"http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s7235_1_1_0_1.html",
    "2016": u"http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s6472_1_1_0_1.html",
    # "2015": u"http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s6132_1_1_0_1.html", #格式不一样，屏了
    # "2014": u"http://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s5359_1_1_0_1.html"
}


def zol_spider(year):
    wb_name = '%s.xls' % year
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet("zol", cell_overwrite_ok=True)

    title_index = {  # 索引参数的列
        '机型': 0,
        '价格': 1,
        '4G网络': 2,
        '屏幕': 3,
        'CPU': 4,
        '主频': 5,
        '电池': 6,
        '操作系统': 7,
        'RAM': 8,
        'ROM': 9,
        '主摄像头': 10,
        # 以上是概要列表页的基础信息，不要动。

        '摄像头总数': 11,    # 左边键可以随便起，好记即可，右边的数字11对应 上面的 摄像头总数。
        '前置摄像头': 12,
        '传感器': 13,
        '闪光灯': 14,
        '光圈': 15,
        '焦距': 16,
        '广角': 17,
        '视频拍摄': 18,
        '摄像头认证': 19,
        '摄像头特色': 20,
        '拍照功能': 21,
        '其他摄像头参数': 22,
    }

    if len(title_index) != len(set(title_index)):
        raise ValueError('titles has duplicates.')

    for __column in title_index:
        sheet.write(0, title_index[__column], __column)
    wb.save(wb_name)

    rows = 1  # excel 行数索引

    detail_domain = "http://detail.zol.com.cn"

    head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    url = urls[year]
    req = Request(url, headers=head)
    response = urlopen(req)
    html = response.read().decode('gbk')
    # print html
    soup = BeautifulSoup(html, 'html.parser')
    total_page_area = soup.find('div', class_="page_total")  # 获取页面区域的信息
    __pages = re.findall(u"/(\d*) 页", total_page_area.text)  # 获取总页码

    if len(__pages) == 1:
        total_page = int(__pages[0])
        print "Total pages: %s" % total_page
    else:
        print 'get total pages failed.total %s' % len(__pages)
        sys.exit(-1)

    # 生成所有待爬的网页
    url_templet = url.replace('1.html', '')

    unknown_list = []

    for each_page in range(total_page):  # 遍历，开爬
        print "page: ", each_page + 1
        per_url = "%s%s%s" % (url_templet, each_page + 1, ".html")
        req = Request(per_url, headers=head)
        response = urlopen(req)
        html = response.read().decode('gbk')
        soup = BeautifulSoup(html, 'html.parser')
        result_frame = soup.find("ul", class_="result_list")  # 包含搜索信息的那个框架

        phones = result_frame.find_all("li")  # 匹配出单个手机的信息
        for phone_content in phones:
            try:  # 获取价格
                phone_name = phone_content.find("dl", class_="pro_detail").find("a").text
                phone_price = phone_content.find("div", class_="date_price").find("b", class_="price-type").text
                sheet.write(rows, title_index['机型'], phone_name)
                sheet.write(rows, title_index['价格'], phone_price)

            except:
                continue

            details = phone_content.find_all("li")
            for i in details:

                if u'4G网络' in str(i):
                    sheet.write(rows, title_index['4G网络'], i["title"])
                elif u'主屏尺寸' in str(i):
                    sheet.write(rows, title_index['屏幕'], i["title"])
                elif u'CPU型号' in str(i):
                    sheet.write(rows, title_index['CPU'], i["title"])
                elif u'CPU频率' in str(i):
                    sheet.write(rows, title_index['主频'], i["title"])
                elif u'电池容量' in str(i):
                    sheet.write(rows, title_index['电池'], i["title"])
                elif u'出厂系统' in str(i):
                    sheet.write(rows, title_index['操作系统'], i["title"])
                elif u'RAM容量' in str(i):
                    sheet.write(rows, title_index['RAM'], i["title"])
                elif u'ROM容量' in str(i):
                    sheet.write(rows, title_index['ROM'], i["title"])
                elif u'后置摄像' in str(i):
                    sheet.write(rows, title_index['主摄像头'], i["title"])

            detail_url = phone_content.find("a", target="_blank")["href"]
            phone_detail_url = detail_domain + detail_url
            req = Request(phone_detail_url, headers=head)
            response = urlopen(req)
            html = response.read().decode('gbk')
            soup = BeautifulSoup(html, 'html.parser')

            # 以下是获取摄像头表格的代码↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            tds = soup.find('td', class_="hd", text=u'摄像头')  # 表格标题
            try:
                camera_area = tds.parent.parent  # 摄像头总表格
            except:
                print "can not get camera info: ", phone_detail_url
                rows += 1
                continue
            for tr in camera_area.find_all('tr'):
                try:
                    if tr.th.text == u'摄像头总数':
                        sheet.write(rows, title_index['摄像头总数'], tr.td.span.contents[0])
                    elif tr.th.text == u'前置摄像头':
                        sheet.write(rows, title_index['前置摄像头'], tr.td.span.contents[0])
                    elif tr.th.text in [u'传感器类型', u'传感器型号']:
                        sheet.write(rows, title_index['传感器'], tr.td.span.contents[0])
                    elif tr.th.text == u'闪光灯':
                        sheet.write(rows, title_index['闪光灯'], tr.td.span.contents[0])
                    elif tr.th.text == u'焦距/范围':
                        sheet.write(rows, title_index['焦距'], tr.td.span.contents[0])
                    elif tr.th.text in [u'光圈', u'\n光圈\n']:
                        sheet.write(rows, title_index['光圈'], tr.td.span.contents[0])
                    elif tr.th.text in [u'广角']:
                        sheet.write(rows, title_index['广角'], tr.td.span.contents[0])
                    elif tr.th.text == u'视频拍摄':
                        sheet.write(rows, title_index['视频拍摄'], tr.td.span.contents[0])
                    elif tr.th.text == u'拍照功能':
                        sheet.write(rows, title_index['拍照功能'], tr.td.span.text)
                    elif tr.th.text == u'摄像头认证':
                        sheet.write(rows, title_index['摄像头认证'], tr.td.span.text)
                    elif tr.th.text == u'摄像头特色':
                        sheet.write(rows, title_index['摄像头特色'], tr.td.span.text)
                    elif tr.th.text == u'其他摄像头参数':
                        sheet.write(rows, title_index['其他摄像头参数'], tr.td.span.contents[0])
                    elif tr.th.text == u'后置摄像头':
                        pass
                    else:
                        if tr.th.text not in unknown_list:
                            print 'new parm: ', tr.th.text, phone_detail_url
                            unknown_list.append(tr.th.text)
                except:
                    pass  # 大表格外面的标题为none，会报错
            # 获取摄像头的代码结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

            wb.save(wb_name)
            rows += 1
            sleep_time = random.randint(1, 3)  # 定义一个随机睡眠时间，防止被识别为爬虫，可能有点作用。
            # time.sleep(sleep_time)


if __name__ == "__main__":
    # zol_spider(2019)
    if len(sys.argv) <= 1:
        zol_spider("2019")
    elif sys.argv[1] in urls.keys():
        zol_spider(sys.argv[1])
    else:
        print('wrong argument, only support [2016-2019]')
