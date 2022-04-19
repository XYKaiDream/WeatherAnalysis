#!/usr/bin/python
# coding=utf-8
import re
from flask import Flask, render_template, jsonify, request, url_for
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
from sklearn.metrics import mean_squared_error

from database import is_existed, add_user, getpasswd
from flask import redirect
app = Flask(__name__)
app.config.from_object('config')

# 郑州空气质量数据
weather_df = pd.read_csv(open("beijing_weather.csv", 'rb'), encoding='utf-8', error_bad_lines=True)
# weather_df = pd.read_csv('beijing_weather.csv','rb')
del weather_df['Unnamed: 0']
weather_df['天气状况'] = weather_df['天气状况'].map(lambda x: x.split('/')[0])
# 且分出最高气温和最低气温
weather_df['最高气温'] = weather_df['气温'].map(lambda x: float(x.split('/')[0][:-1]))
weather_df['最低气温'] = weather_df['气温'].map(lambda x: float(x.split('/')[1][:-1]))

# 切分出最大风力风向和最小风力风向
weather_df['最大风力风向'] = weather_df['风力风向'].map(lambda x: x.split('/')[0])
weather_df['最小风力风向'] = weather_df['风力风向'].map(lambda x: x.split('/')[1])
# 从日期中切分出 年、月，替换为 -，2017年01月01日  --> 2017-01-01
weather_df['日期'] = weather_df['日期'].map(lambda x: x.replace('年', '-').replace('月', '-').replace('日', ''))
weather_df['年'] = weather_df['日期'].map(lambda x: int(x.split('-')[0]))
weather_df['月'] = weather_df['日期'].map(lambda x: int(x.split('-')[1]))
del weather_df['气温']
del weather_df['风力风向']

print(weather_df.head(5))


# --------------- 页面 ---------------
@app.route('/')
def index():
    return redirect(url_for('user_login') )
    # return render_template('index.html')

@app.route('/history_weather/?<string:account>')
def history_weather(account):
    return render_template('history_weather.html',account = account)


@app.route('/weather_date_horizontal')
def weather_date_horizontal():
    return render_template('weather_date_horizontal.html')


@app.route('/month_weather_in_different_year')
def month_weather_in_different_year():
    return render_template('month_weather_in_different_year.html')

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    # user information submitted methods must be POST
    if request.method=='POST':  # 注册发送的请求为POST请求
        # get the user information that user submitted
        username = request.form['username']
        password = request.form['password']
        print(password,username)
        # if the information is correct(in our database)
        if is_existed(username, password):
            # return render_template('layout.html',account=username)
            return redirect(url_for('history_weather',account=username))
            # return  render_template('history_weather.html')
        else:
            login_massage = "登陆失败，请检查用户名与密码"
            return render_template('index.html', message=login_massage)
        # return render_template('index.html')
    else:
        # login_massage = "请求失败"
        return render_template('index.html')

@app.route('/acceptpasswd',methods=['GET','POST'])
def acceptpasswd():
    if request.method=='POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        if getpasswd(username, email, phone):
            login_massage = '你的密码为:'+getpasswd(username, email, phone)[1][0][0]
            return render_template('acceptpasswd.html',message = login_massage)
        else:
            login_massage = "找回失败，请重新输入"
            return render_template('acceptpasswd.html', message=login_massage)
    return render_template('acceptpasswd.html')

@app.route("/register",methods=["GET", 'POST'])
def register():
    if request.method == 'POST':
        if re.match(r"^1[35678]\d{9}$", request.form['phone'])!=None:
            if re.match(r'^[1-9][0-9]{4,10}@.*?\.com',request.form['mail'])!=None:
                add_user(request.form['username'], request.form['password'],request.form['phone'],request.form['mail'])
                return redirect('/')
            else:
                login_massage = "邮箱格式不正确，请重新输入"
                return render_template('register.html', message_mail=login_massage)
        else:
            login_massage = "手机格式不正确，请重新输入"
            return render_template('register.html', message=login_massage)
    return render_template('register.html')

# --------------- API 接口 ---------------
@app.route('/get_all_yearmonths')
def get_all_yearmonths():
    year = list(sorted(set(weather_df['年'])))[::-1]
    month = list(sorted(set(weather_df['月'])))[::-1]
    return jsonify({'year': year, 'month': month})


@app.route('/get_weather_by_year_month/<year>/<month>')
def get_city_air_quality(year, month):
    df = weather_df[(weather_df['年'] == int(year)) & (weather_df['月'] == int(month))]
    df = df.sort_values(by='日期', ascending=True)
    df = df[['日期', '天气状况', '最高气温', '最低气温', '最大风力风向', '最小风力风向']]
    # print(df.shape)
    return jsonify(df.values.tolist())


@app.route('/get_air_quality_by_city_year/<city>/<year>/<zhibiao>')
def get_air_quality_by_city_year(city, year, zhibiao):
    city_df = weather_df[(weather_df['city'] == city) & (weather_df['year'] == year)]
    city_df = city_df.sort_values(by='time', ascending=True)
    print('数据条目数：', city_df.shape[0])
    return jsonify({'time': city_df['time'].values.tolist(),
                    'data': city_df[zhibiao].values.tolist()})


@app.route('/analysis_weather_year1_year2/<start_year>/<end_year>')
def analysis_weather_year1_year2(start_year, end_year):
    """开始结束年间的天气变化分析"""
    start_year, end_year = int(start_year), int(end_year)
    df = weather_df[(weather_df['年'] >= start_year) & (weather_df['年'] <= end_year)]
    df = df.sort_values(by='日期', ascending=True)
    times = df['日期'].values.tolist()
    high_temp = df['最高气温'].values.tolist()
    low_temp = df['最低气温'].values.tolist()

    # 天气状况
    tianqi_counts = df['天气状况'].value_counts().reset_index()
    # 风力与风向
    feng_counts = df['最大风力风向'].value_counts().reset_index()
    return jsonify({'日期': times, '最高气温': high_temp, '最低气温': low_temp,
                    '天气状况': tianqi_counts['index'].values.tolist(),
                    '天气状况_个数': tianqi_counts['天气状况'].values.tolist(),
                    '风力风向': feng_counts['index'].values.tolist()[::-1],
                    '风力风向_个数': feng_counts['最大风力风向'].values.tolist()[::-1]})


@app.route('/get_city_calendar_data/<year>')
def get_city_calendar_data(year):
    df = weather_df[weather_df['年'] == int(year)]
    df = df.sort_values(by='日期', ascending=True)

    max_zhibiao = max((df['最高气温'] + df['最低气温']) / 2)

    results = {}
    times = df['日期'].values.tolist()
    zhibiao_values = ((df['最高气温'] + df['最低气温']) / 2).values.tolist()
    data = {}
    for i in range(df.shape[0]):
        data[times[i]] = zhibiao_values[i]
    results[year] = data
    print(results)
    results['最大值'] = max_zhibiao
    results['年份'] = [year]
    return jsonify(results)


@app.route('/month_weather_in_year_analysis/<month>')
def month_weather_in_year_analysis(month):
    years = [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
    month = int(month)
    high_temp = []
    low_temp = []
    for year in years:
        df = weather_df[(weather_df['年'] == year) & (weather_df['月'] == month)]
        high_temp.append(df['最高气温'].values.mean())
        low_temp.append(df['最低气温'].values.mean())
    return jsonify({'年份': years, '月平均最高气温': high_temp, '月平均最低气温': low_temp})


if __name__ == "__main__":
    app.run()
