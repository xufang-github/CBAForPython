import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
from random import uniform
import logging

class BinanceNewsSpider:
    def __init__(self):
        self.news_url = "https://www.binance.com/zh-CN/square/news/all"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Referer": "https://www.binance.com/"
        }
        self.processed_news = set()
        self.last_request_time = 0
        self.min_request_interval = 2
        
        # 配置日志
        self.logger = logging.getLogger('BinanceNewsSpider')
        self.logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler('binance_spider.log', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # 添加处理器到日志记录器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        self.logger.info("BinanceNewsSpider initialized")

    def _wait_for_rate_limit(self):
        """确保请求间隔足够长"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed + uniform(0.1, 0.5)
            self.logger.debug(f"Waiting {sleep_time:.2f}s for rate limit")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get_news(self):
        """获取币安新闻列表"""
        try:
            self.logger.info("Starting to fetch news")
            self._wait_for_rate_limit()
            
            self.logger.debug(f"Sending request to {self.news_url}")
            response = requests.get(self.news_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.debug("Successfully parsed HTML content")
            
            # 直接查找所有新闻块
            news_divs = soup.find_all('div', class_='css-vurnku')
            self.logger.info(f"Found {len(news_divs)} news items in total")
            
            news_items = []
            new_count = 0
            skip_count = 0
            
            for news_div in news_divs:
                try:
                    # 获取新闻链接
                    news_link = news_div.find('a', style='display:block;margin-bottom:8px')
                    if not news_link:
                        continue
                    
                    # 获取标题
                    title_element = news_link.find('h3', class_='css-yxpvu')
                    if not title_element:
                        continue
                    title = title_element.text.strip()
                    
                    # 获取内容
                    content_element = news_link.find('div', class_='css-10lrpzu')
                    content = content_element.text.strip() if content_element else ""
                    
                    # 如果新闻已处理过，跳过
                    if title in self.processed_news:
                        skip_count += 1
                        self.logger.debug(f"Skipping processed news: {title}")
                        continue
                    
                    # 获取链接
                    url = "https://www.binance.com" + news_link.get('href', '')
                    
                    # 获取时间
                    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    news_item = {
                        "title": title,
                        "content": content,
                        "url": url,
                        "time": time_str
                    }
                    
                    news_items.append(news_item)
                    self.processed_news.add(title)
                    new_count += 1
                    
                    self.logger.info(f"New news found: {title}")
                    self.logger.debug(f"News details: {json.dumps(news_item, ensure_ascii=False)}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing news item: {str(e)}", exc_info=True)
                    continue
            
            self.logger.info(f"Fetch completed. {new_count} new items, {skip_count} skipped")
            return news_items
            
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}", exc_info=True)
            return []
