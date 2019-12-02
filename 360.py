#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2019/11/20 14:50
# @Author  : 陈浩基
# @FileName: 360.py
# @Software: PyCharm
from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
import os
import shutil
import glob
import requests

startTime = '2019-11-29'
endTime = '2019-11-29'
pageNum = 2  # 爬取页数


def get_html(browser):
    browser.get("https://shangyi.360.cn/")
    # 登录
    browser.execute_script(
        "document.getElementsByClassName('quc-input quc-input-account')[0].value='账号")
    browser.execute_script("document.getElementsByClassName('quc-input quc-input-password')[0].value='密码'")
    # 登录需要验证码
    # input('====================输入验证码后回车====================')
    browser.execute_script(
        "document.getElementsByClassName('quc-submit quc-button quc-button-primary quc-button-sign-in')[0].click()")
    time.sleep(5)
    cookies = browser.get_cookie('thinkjs')
    print('thinkjs=' + cookies['value'])
    # 查看运行成功列表
    browser.execute_script(
        "document.querySelector('#main > div:nth-child(3) > div > div.query-conditions.fs12 > label:nth-child(4) > ui-select > div > div.select_drop > div:nth-child(2)').click()")
    for i in range(pageNum):
        time.sleep(5)  # 等待页面加载完成
        taskMap = get_task_id(browser.page_source)
        print('====================获取第{}页Id列表成功===================='.format(i))
        download_file(browser, taskMap, startTime, endTime)
        browser.execute_script("document.getElementsByClassName('page-next ng-scope')[0].click()")  # 下一页


def get_task_id(html):
    bs_html = bs(html, 'html5lib')
    ids = bs_html.find_all('tr', attrs={'class': 'job-finished'})
    taskMap = dict()
    for id in ids:
        idMap = dict()
        taskName = id.find_all('td', attrs={'class': 'ng-binding'})[0].get_text().replace(' ', '').replace('\n', '')
        submitTime = id.find_all('td', attrs={'class': 'ng-binding'})[1].get_text().split(' ')[0]
        taskId = id.find_all('td', attrs={'class': 'ops'})[0].find_all('a')[0]['href'].split('/')[-1]
        idMap[taskId] = submitTime
        taskMap[taskName] = idMap
    return taskMap


def download_file(browser, task_map, start_time, end_time):
    tags = ['interest_point', 'people_tag', 'people_property', 'gouwu_interest_point', 'query_dstrb',
            'active_app_dstrb']
    url = 'https://shangyi.360.cn/report/download?data_from=pc&jobid={}&datatag={}'
    i = 0
    task_map_len = len(task_map)
    for taskName, idMap in task_map.items():
        for k, v in idMap.items():
            i += 1
            if start_time <= v <= end_time:
                path = os.getcwd() + '\excel\\'
                if not os.path.exists(path + taskName):
                    os.mkdir(path + taskName)
                print('进度：{}/{}，当前任务名：{}，id名：{}'.format(i, task_map_len, taskName, k))
                for tag in tags:
                    browser.get(url.format(k, tag))
                    time.sleep(5)  # 防止出现文件还没下载完的情况
                    move_file(taskName)  # 转移到任务名所属文件夹
            else:
                print('进度：{}/{}，任务时间不符，跳过'.format(i, task_map_len))


def move_file(task_name):
    path = os.getcwd() + '\excel\\'
    while True:
        list_of_files = glob.glob(path + '*')
        latest_file = max(list_of_files, key=os.path.getctime)
        if latest_file.split('.')[-1] == 'xls':
            break
    shutil.move(latest_file, path + task_name)


def download_data(cookies, task_id):
    url = 'https://shangyi.360.cn/report/request/?para={{"id":{},"compare":0,"ids":{},"data_from":"pc"}}&path=ReportBrandTrendsPicture'
    referer = 'https://shangyi.360.cn/report/brand_trend/{}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Accept': 'application/json, text/plain, */*', 'Host': 'shangyi.360.cn', 'Referer': referer.format(task_id),
        'Cookie': cookies}
    data = requests.get(url=url.format(task_id, task_id), headers=headers)
    data = data.json()
    return data['data']


if __name__ == '__main__':
    # options = webdriver.ChromeOptions()
    # # 开发者模式对抗识别
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # # 禁止弹窗和下载路径
    # prefs = {"download.default_directory": os.getcwd() + "\excel\\",
    #          "download.prompt_for_download": False}
    # options.add_experimental_option('prefs', prefs)
    # # 无头模式，无验证码可以使用
    # # options.add_argument('--headless')
    # browser = webdriver.Chrome('.\\chromedriver.exe', options=options)
    # get_html(browser)
    # browser.close()
    print(download_data('thinkjs=GPnW3wKlX1qMM7psjc7Ti_qdpSq_YVOY.rQ6QyysnVPQ257H%2B2GpgEYyO64CJVhazCa7kY71k6%2F0',
                        88399))
