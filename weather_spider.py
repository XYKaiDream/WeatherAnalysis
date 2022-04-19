#!/usr/bin/python
# _*_ coding: utf-8 _*_

"""
气温数据爬取
"""
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import pymysql

# remove space
from sqlalchemy import create_engine

spaces = {'\x10', '\x7f', '\x9d', '\xad', '\\x0a', '\\xa0', '\\x0d',
          '\f', '\n', '\r', '\t', '\v', '&#160;', '&nbsp;',
          '\u200b', '\u200e', '\u202a', '\u202c', '\ufeff', '\uf0d8', '\u2061', '\u1680', '\u180e',
          '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005', '\u2006', '\u2007', '\u2008',
          '\u2009', '\u200a', '\u2028', '\u2029', '\u202f', '\u205f', '\u3000'}


def remove_space(text):
    for space in spaces:
        text = text.replace(space, '')
    text = text.strip()
    text = re.sub('\s+', '', text)  # 正则表达式替换多个空白字符为空字符
    return text


# years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]
years = [2020]
# months = list(range(1, 13))
months = list(range(1, 2))

all_date = []
all_tianqi = []
all_qiwen = []
all_feng = []

year_months = []
for year in years:
    for month in months:
        year_months.append('{}{}'.format(year, month if month > 9 else '0{}'.format(month)))

for year_month in year_months:
    print('爬取 {} 的气温数据'.format(year_month))
    url = 'http://www.tianqihoubao.com/lishi/beijing/month/{}.html'.format(year_month)
    response = requests.get(url)
    response = response.text

    soup = BeautifulSoup(response, 'lxml')
    items = soup.table.find_all('tr')

    for i, item in enumerate(items):
        if i == 0:
            continue

        try:
            data = item.find_all('td')

            date = remove_space(data[0].text)
            tianqi = remove_space(data[1].text)
            qiwen = remove_space(data[2].text)
            feng = remove_space(data[3].text)

        except:
            continue

        all_date.append(date)
        all_tianqi.append(tianqi)
        all_qiwen.append(qiwen)
        all_feng.append(feng)

weather_df = pd.DataFrame({'日期': all_date, '天气状况': all_tianqi, '气温': all_qiwen, '风力风向': all_feng})
# print(weather_df)
con = pymysql.connect(host='localhost', port=3306, database="datademo", user='root', password='123456')
conn = create_engine('mysql+pymysql://root:123456@localhost:3306/datademo?charset=utf8')
weather_df.to_sql("beijing",con,if_exists='append',index=False)
# weather_df.to_csv('beijing_weather.csv', encoding='utf8')

