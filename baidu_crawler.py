import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

db_path = 'news.db'  # 使用相对路径，数据库文件放在当前脚本目录下

def get_baidu_news():
    url = 'https://top.baidu.com/board'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    news_list = []
    for item in soup.select('.c-single-text-ellipsis'):
        news = item.get_text().strip()
        if news not in news_list:
            news_list.append(news)
    return news_list[:10]

def save_to_db(news_list):
    conn = sqlite3.connect(db_path)  # 使用相对路径创建数据库文件
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, title TEXT, date TEXT)''')

    # 获取当前日期时间
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 插入前检查是否存在相同的新闻标题
    for news in news_list:
        c.execute('SELECT * FROM news WHERE title = ?', (news,))
        if c.fetchone() is None:
            c.execute('INSERT INTO news (title, date) VALUES (?, ?)', (news, date_str))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    news = get_baidu_news()
    save_to_db(news)
