import requests
import configparser
import os
import time
import pandas as pd

GET_ID_URL = 'https://shangyi.360.cn/task/list?page={}&n=30&objectType=all&analysisType=all&dataSource=all&kw=%25&jobStatus=all&report_analysis_type=1&select_id='
DOWNLOAD_FILE_URL = 'https://shangyi.360.cn/report/download?data_from=pc&jobid={}&datatag={}'
DOWNLOAD_DATA_URL = 'https://shangyi.360.cn/report/request/?para={{"id":{},"compare":0,"ids":{},"data_from":"pc"}}&path=ReportBrandTrendsPicture'
TAGS = {"兴趣分布.xls": "interest_point", "人群标签.xls": "people_tag", "人口属性分布.xls": "people_property",
        "购物兴趣分布.xls": "gouwu_interest_point", "搜索词分布.xls": "query_dstrb",
        "APP活跃分布.xls": "active_app_dstrb"}


def get_task_id(page_num):
    referer = 'https://shangyi.360.cn/task/index'
    headers['Referer'] = referer
    job_map = dict()
    for i in range(1, page_num + 1):
        data = requests.get(url=GET_ID_URL.format(i), headers=headers)
        data = data.json()
        for job in data['data']['job_list']:
            id_map = dict()
            job_name = job['job_name']
            modify_time = job['modify_time']
            job_id = job['id']
            id_map[job_id] = modify_time
            job_map[job_name] = id_map
    return job_map


def download_file(path, job_id):
    for k, v in TAGS.items():
        r = requests.get(url=DOWNLOAD_FILE_URL.format(job_id, v), headers=headers)
        with open(path + k, 'wb') as file:
            file.write(r.content)
        time.sleep(1)


def get_data(job_id):
    referer = 'https://shangyi.360.cn/report/brand_trend/{}'
    headers['Referer'] = referer.format(job_id)
    data = requests.get(url=DOWNLOAD_DATA_URL.format(job_id, job_id), headers=headers)
    data = data.json()
    return data['data']['brand_trends_picture'][0]


if __name__ == '__main__':
    config = configparser.RawConfigParser()
    config.read("config.ini", encoding="utf-8")
    page_num = config.get('360', 'pageNum')
    start_time = config.get('360', 'startTime')
    end_time = config.get('360', 'endTime')
    cookies = config.get('360', 'cookies')
    excel_path = os.getcwd() + '\\excel\\'
    brand_trend_path = os.getcwd() + '\\brand_trend\\'
    global headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
        'Accept': 'application/json, text/plain, */*', 'Host': 'shangyi.360.cn', 'Cookie': cookies}
    job_map = get_task_id(2)
    i = 0
    job_map_len = len(job_map)
    for job_name, j in job_map.items():
        for job_id, modify_time in j.items():
            i += 1
            if start_time <= modify_time.split(' ')[0] <= end_time:
                if not os.path.exists(excel_path + job_name):
                    os.mkdir(excel_path + job_name)
                download_file(excel_path + job_name + '\\', job_id)
                print('进度：{}/{}，当前任务名：{}，id名：{}'.format(i, job_map_len, job_name, job_id))
                time.sleep(2)
            else:
                print('进度：{}/{}，任务时间不符，跳过'.format(i, job_map_len))
            brand_trends_picture = get_data(job_id)
            is_exist = False
            if os.path.exists(brand_trend_path + brand_trends_picture['bag_name'] + '.csv'):
                is_exist = True
            df = pd.DataFrame(brand_trends_picture['content'], columns=['date', 'pv'])
            if is_exist:
                df.to_csv(brand_trend_path + brand_trends_picture['bag_name'] + '.csv', mode='a', index=False,
                          header=None)
                csv = pd.read_csv(brand_trend_path + brand_trends_picture['bag_name'] + '.csv', encoding='utf-8')
                data = csv.drop_duplicates(subset=['date'], keep='first')
                data.to_csv(brand_trend_path + brand_trends_picture['bag_name'] + '.csv', index=False)
            else:
                df.to_csv(brand_trend_path + brand_trends_picture['bag_name'] + '.csv', index=False)
