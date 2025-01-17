import socket
import threading
import time
import json

#登录监听器接口
class LoginListener:
    def on_login(self,message):
        pass
#消息监听器接口
class MessageListener:
    def on_message(self, user_name,topic, message):
        pass

class TcpClient:
    def __init__(self, ip, port):
        self.ip = ip        #服务器ip    #服务器ip                                   


class TcpClient(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.ip = ip        #服务器ip                                   
        self.port = port    #服务器端口
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.is_connected = False
        self.is_exit = False
        self.user_name = ""
        self.password = ""
        self.topics = []
        self.bytes_buffer = b''
        self.login_listener = []
        self.message_listener = []

    def connect(self):
        try:
            self.sock.connect((self.ip, self.port))
            self.connect_success()
        except Exception as e:
            self.connect_failed()

    def connect_failed(self):
        print("连接失败")
        self.is_connected = False
        #当前线程休眠10s
        time.sleep(10)   #休眠1s

    def connect_success(self):
        self.is_connected = True
        #连接成功后，发送登录消息
        self.send_login(self.user_name, self.password)
        #订阅所有主题
        for topic in self.topics:
            self.send_subscribe(topic)
        print("连接成功")

    def run(self):
        print("启动客户端线程")
        self.connect()
        while not self.is_exit:
            try:
                #断线重连
                if not self.is_connected:
                    self.connect()
                #阻塞 等待接收数据
                data = self.sock.recv(102400)
                if not data:
                    print("服务器断开连接")
                    self.is_connected = False
                    self.connect()
                else:
                    self.handle_data(data)
            except Exception as e:
                #超时
                if e.args[0] != "timed out":
                    e.print_exc()
                    print("接收数据失败:", e)
                pass
        print("客户端线程结束")


    def handle_data(self, data):
        #收到数据
        print("收到数据:", data)
        #处理接收到的消息
        self.bytes_buffer += data
        #解析消息头
        offfset = 0
        while offfset < len(self.bytes_buffer):
            if len(self.bytes_buffer) < 4:
                break
            header = self.bytes_buffer[offfset:offfset+4]
            #反转header
            header = header[::-1]
            length = int.from_bytes(header, byteorder='big')
            length = self.uint32_to_int32(length)
            print("消息长度:", length)
            if len(self.bytes_buffer) < 4+length:                                       #消息头+消息体+消息尾+校验和
                break
            #解析消息
            msg = json.loads(self.bytes_buffer[offfset+4:offfset+4+length].decode('utf8'))
            print("消息:", msg)
            #根据消息类型进行处理
            if msg["type"] == "login":
                self.handle_login(msg)
            elif msg["type"] == "logout":
                self.handle_logout( msg)
            elif msg["type"] == "subscribe":
                self.handle_subscribe( msg)
            elif msg["type"] == "message":
                self.handle_message(msg)


            else:
                print("未知消息类型")
            #删除已处理的消息
            self.bytes_buffer = self.bytes_buffer[offfset+4+length+4:]
            offfset = 0

    def handle_login(self, msg):
        print("登录消息:", msg)
        #遍历登录监听器，通知登录成功
        for listener in self.login_listener:
            listener.on_login(msg["message"])

    def handle_logout(self, msg):
        print("登出消息:", msg)

    def handle_subscribe(self, msg):
        print("订阅消息:", msg)

    def handle_message(self, msg):
        #遍历消息监听器，通知消息
        for listener in self.message_listener:
            listener.on_message(msg["userName"],msg["topic"], msg["message"])

    def send_login(self, user_name, password):
        self.user_name = user_name
        self.password = password
        #检查 用户名和密码是否为空
        if(user_name == "" or password == ""):
            return
        #发送登录消息
        msg = {"type":"login", "userName":user_name, "password":password}
        self.send_message_self(msg)

    def send_logout(self, user_name):
        #发送登出消息
        msg = {"type":"logout", "userName":user_name}
        self.send_message_self(msg)

    def send_subscribe(self, topic):
        if(topic in self.topics):
            return
        self.topics.append(topic)
        #发送订阅消息
        msg = {"type":"subscribe", "topic":topic}
        self.send_message_self(msg)

    def send_message(self, topic, message):
        #发送消息消息   
        msg = {"type":"message", "topic":topic, "message":message}
        self.send_message_self(msg)

    def to_uint32(self,val):
        return val & 0xFFFFFFFF
    
    def uint32_to_int32(self,uint32_value):
        if uint32_value <= 0x7FFFFFFF:
            return uint32_value  # No conversion needed for positive values
        else:
            return uint32_value - 0x100000000 

    def send_message_self(self, msg):
        msg.update({"userName":self.user_name})
        #拼接消息头、消息体、消息
        if not self.is_connected:
            print("未连接服务器")
            return
        body = json.dumps(msg).encode('utf8')
        header = self.to_uint32(len(body)).to_bytes(4, byteorder='big')
        #反转header
        header = header[::-1]
        data = header + body
        #发送消息
        try:
            self.sock.sendall(data)
        except Exception as e:
            print("发送数据失败:", e)

    def exit(self):
        self.is_exit = True
        self.sock.close()
        print("退出程序")
    
    def add_login_listener(self, listener):
        self.login_listener.append(listener)

    def add_message_listener(self, listener):    
        self.message_listener.append(listener)

    def remove_login_listener(self, listener):
        self.login_listener.remove(listener)

    def remove_message_listener(self, listener):    
        self.message_listener.remove(listener)