import MyTcpClient

    
    

if __name__ == '__main__':
    import json
    client = MyTcpClient.TcpClient("123.249.105.160", 8080)
    client.start()

    #登录监听器
    class MyLoginListener(MyTcpClient.LoginListener):
        def on_login(self,message):
            print("登录结果:",message)

    #消息监听器
    class MyMessageListener(MyTcpClient.MessageListener):
        def on_message(self, user_name, topic, message):
            print("收到消息:", user_name, topic, message)

    client.add_login_listener(MyLoginListener())
    client.add_message_listener(MyMessageListener())


    while True:
        operation = input("请输入操作(login, logout, subscribe, message, exit):\n")
        if operation == "login":
            user_name = input("请输入用户名:")
            password = input("请输入密码:")
            client.send_login(user_name, password)
        elif operation == "logout":
            user_name = input("请输入用户名:")
            client.send_logout(user_name)
        elif operation == "subscribe":
            topic = input("请输入主题:")
            client.send_subscribe(topic)
        elif operation == "message":
            topic = input("请输入主题:")
            message = input("请输入消息:")
            client.send_message(topic, message)
        elif operation == "exit":
            client.exit()
            break
        else:
            print("未知操作")
    client.join()    #等待线程结束