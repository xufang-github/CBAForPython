import time
from binance_news_spider import BinanceNewsSpider
from MyTcpClient import TcpClient
import json

def main():
    # 初始化爬虫和TCP客户端
    spider = BinanceNewsSpider()
    tcp_client = TcpClient("123.249.105.160", 8080)
    # 公布主题
    tcp_client.send_subscribe("binance_news")
    # 登录
    login_success = tcp_client.send_login("萧漠", "olqf1995")
    tcp_client.start()
    
    while True:
        try:
            # 获取新闻
            news_items = spider.get_news()
            # 发送新闻
            for news in news_items:
                message = json.dumps(news)
                print(message)
                success = tcp_client.send_message("binance_news",message)
                if success:
                    print(f"Sent news: {news['title']}")
                else:
                    print(f"Failed to send news: {news['title']}")
            
            # 等待500毫秒
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error in main loop: {str(e)}")
            time.sleep(1)  # 发生错误时等待1秒再继续

if __name__ == "__main__":
    main()
