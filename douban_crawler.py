import requests
from bs4 import BeautifulSoup
import sqlite3
import os

import logging
logging.basicConfig(level=logging.INFO)

db_path = os.path.join(os.path.dirname(__file__), 'douban_movies.db')
# db_path = 'douban_movies.db'

# 获取页面内容
def get_page(url):
    logging.info(f'正在请求 URL: {url}')

    # 使用代理避免被识别为爬虫
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # response = requests.get(url, headers=headers)
    # return response.content
    try:
        response = requests.get(url, headers=headers)
        logging.info(f'收到响应，状态码: {response.status_code}')
        response.raise_for_status()
        return response.content
    except Exception as e:
        logging.error(f'请求失败: {e}')
        return None

# 解析页面内容
def parse_page(content):
    soup = BeautifulSoup(content, 'html.parser')
    movies = []
    for item in soup.find_all('div', class_='item'):
        title = item.find('span', class_='title').text
        info = item.find('p', class_='').text.strip().split('\n')
        director = info[0].strip().split(' ')[1]
        countries = info[1].strip().split('/')[1].strip()
        movies.append({'title': title, 'countries': countries, 'director': director})
    return movies

# 爬取豆瓣Top 100电影
def scrape_douban_top100():
    base_url = 'https://movie.douban.com/top250?start='
    all_movies = []
    # 每页显示25个电影，总共爬取100个
    for i in range(0, 100, 25):
        url = base_url + str(i)
        content = get_page(url)
        movies = parse_page(content)
        all_movies.extend(movies)
    return all_movies

def save_to_db(movies):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY,
            title TEXT,
            director TEXT,
            countries TEXT
        )
    ''')
    for movie in movies:
        # 检查数据库中是否已有此电影
        c.execute('SELECT id, countries FROM movies WHERE title = ? AND director = ?', (movie['title'], movie['director']))
        result = c.fetchone()
        if result:
            # 如果已存在，将新国家信息合并
            movie_id, existing_countries = result
            existing_countries_set = set(existing_countries.split(','))
            new_countries_set = set(movie['countries'])
            updated_countries_set = existing_countries_set.union(new_countries_set)
            updated_countries = ','.join(sorted(updated_countries_set))  # 去重并排序
            c.execute('UPDATE movies SET countries = ? WHERE id = ?', (updated_countries, movie_id))
        else:
            c.execute('INSERT INTO movies (title, director, countries) VALUES (?, ?, ?)', (movie['title'], movie['director'], movie['countries']))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    movies = scrape_douban_top100()
    save_to_db(movies)
