# Flask: 一个用于构建web应用的轻量级框架，用jsonify函数将python数据结构转换为json格式
from flask import Flask, jsonify
import sqlite3
# 解决CORS（跨域资源共享）问题
from flask_cors import CORS
import os
from baidu_crawler import get_baidu_news, save_to_db
from douban_crawler import scrape_douban_top100, save_to_db as save_movies_to_db

app = Flask(__name__)
CORS(app)

news_db_path = 'news.db'
movies_db_path = 'douban_movies.db'

def get_news_from_db():
    # 检查数据库文件是否存在
    if not os.path.exists(news_db_path):
        news_list = get_baidu_news()
        save_to_db(news_list)

    conn = sqlite3.connect(news_db_path)
    c = conn.cursor()
    c.execute('SELECT title FROM news')
    news_list = [row[0] for row in c.fetchall()]
    conn.close()

    # 如果数据库中没有数据，调用爬虫程序
    if not news_list:
        news_list = get_baidu_news()
        save_to_db(news_list)
        conn = sqlite3.connect(news_db_path)
        c = conn.cursor()
        c.execute('SELECT title FROM news')
        news_list = [row[0] for row in c.fetchall()]
        conn.close()

    return news_list

def get_movies_from_db():
    # 检查数据库文件是否存在
    if not os.path.exists(movies_db_path):
        movies_list = scrape_douban_top100()
        save_movies_to_db(movies_list)

    conn = sqlite3.connect(movies_db_path)
    c = conn.cursor()
    c.execute('SELECT title, director, countries FROM movies')
    movies = [{'title': row[0], 'director': row[1], 'countries': row[2]} for row in c.fetchall()]
    conn.close()

    # 如果数据库中没有数据，调用爬虫程序
    if not movies:
        movies = scrape_douban_top100()
        save_movies_to_db(movies)
        conn = sqlite3.connect(movies_db_path)
        c = conn.cursor()
        c.execute('SELECT title, director, countries FROM movies')
        movies = [{'title': row[0], 'director': row[1], 'countries': row[2]} for row in c.fetchall()]
        conn.close()

    return movies

@app.route('/api/news', methods=['GET'])
def get_news():
    news = get_news_from_db()
    return jsonify(news)

@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = get_movies_from_db()
    return jsonify(movies)

if __name__ == '__main__':
    app.run(debug=True)


