#  coding: utf-8 
import socketserver
import os.path

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        # data:
        # Got a request of: b'GET / HTTP/1.1\r\n
        # Host: localhost:8080\r\n
        # User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:96.0) Gecko/20100101 Firefox/96.0\r\n
        # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n
        # Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2\r\n
        # Accept-Encoding: gzip, deflate\r\n
        # Connection: keep-alive\r\n
        # Upgrade-Insecure-Requests: 1\r\n
        # Sec-Fetch-Dest: document\r\n
        # Sec-Fetch-Mode: navigate\r\n
        # Sec-Fetch-Site: none\r\n
        # Sec-Fetch-User: ?1'

        # Decode!!
        # https://stackoverflow.com/questions/41918836/how-do-i-get-rid-of-the-b-prefix-in-a-string-in-python
        method = self.data.split()[0].decode('utf-8')
        # print(req) the result is GET
        if method == "GET":
            dir = self.data.splitlines()[0].split()[1].decode('utf-8')
            # print(dir) the result is /www

            # if the path is a directory
            if dir[-1] == "/":
                # since the test case is under ./www by default
                # thus we need to add "www"
                dir = "www" + dir
                if '..' in dir and not self.path_isvalid(dir):
                    self.Not_Found_404()
                else:
                    dir = dir + "index.html"
                    if not os.path.exists(dir):
                        self.Not_Found_404()
                    else:
                        self.OK_200(dir)

            # if the directory points to a .css or .html file
            elif  dir[-1] != "/":
                if "css" in dir or "html" in dir:
                    dir = "www" + dir
                    if '..' in dir and not self.path_isvalid(dir):
                        self.Not_Found_404()
                    elif not os.path.exists(dir):
                        self.Not_Found_404()
                    else:
                        self.OK_200(dir)
                else:
                    dir = "www" + dir + "/"
                    if '..' in dir and not self.path_isvalid(dir):
                        self.Not_Found_404()
                    elif not os.path.exists(dir):
                        self.Not_Found_404()
                    else:
                        self.Redirect_301(dir)

            elif not os.path.exists("www" + dir):
                self.Not_Found_404()
            else:
                self.OK_200("www" + dir)

        else:
            self.Method_Not_Allowed_405()        
        #self.request.sendall(bytearray("404",'utf-8'))

    # check if the path is a sub directory of ./www
    # https://docs.python.org/3/library/os.path.html
    def path_isvalid(self, dir):
        absPath = os.path.abspath(dir)
        absCommonPath = os.path.abspath("www")
        if os.path.commonpath([absPath, absCommonPath]) != absCommonPath:
            return False
        return True
    
    #reference:https://www.tutorialspoint.com/http/http_responses.htm
    def Not_Found_404(self):
        # TODO: modify the 404 webpage
        # like contant = "404 NOT Found" in CSS
        content = "<html><head><title>404 Not Found</title></head><body><h1>404 Not Found</h1>\
            <p>The requested URL /t.html was not found on this server.</p></body></html>"
        serverResponse = "HTTP/1.1 404 Not Found\r\n"
        contentType = "Content-Type: html\r\n"
        self.sendMsg(serverResponse, contentType, content)

    def OK_200(self, dir):
        serverResponse = "HTTP/1.1 200 OK\r\n"
        contentType = "Content-Type:" + self.get_Content_Type(dir) + "\r\n"
        # TODO modify content
        content = self.getContent(dir)
        self.sendMsg(serverResponse, contentType, content)

    def Redirect_301(self, dir):
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/301
        serverResponse = "HTTP/1.1 301 Moved Permanently\r\n"
        content = "<html><head><title>301 Moved Permanently</title></head><body><h1>301 Moved Permanently</h1></body></html>"
        location = "Location: http://" + str(HOST) + str(PORT) + dir + "\r\n"
        self.request.sendall(bytearray(serverResponse,'utf-8'))
        self.request.sendall(bytearray("Connection: close\r\n\r\n",'utf-8'))
        self.request.sendall(bytearray(content,'utf-8'))
        self.request.sendall(bytearray(location,'utf-8'))

    def sendMsg(self, serverResponse, contentType, content):
        self.request.sendall(bytearray(serverResponse, 'utf-8'))
        self.request.sendall(bytearray("Content-Length:" + str(len(content)) +"\r\n", 'utf-8' ))
        self.request.sendall(bytearray(contentType, 'utf-8'))
        self.request.sendall(bytearray("Connection: Close\r\n\r\n", 'utf-8'))
        self.request.sendall(bytearray(content, 'utf-8'))

    def getContent(self, dir):
        file = open(dir, "r")
        content = ""
        for item in file:
            content = content + item
        file.close()
        return(content)

    def get_Content_Type(self, dir):
        if "html" in dir:
            return "text/html"
        elif "css" in dir:
            return "text/css"
        else:
            return "text"

    def Method_Not_Allowed_405(self):
        content = "<html><head><title>405 Method Not Allowed</title></head><body><h1>Not Found</h1>\
            <p>The requested method is not allowed on this server.</p></body></html>"
        serverResponse = "HTTP/1.1 405 Method Not Allowed\r\n"
        contentType = "Content-Type: html\r\n"
        self.sendMsg(serverResponse, contentType, content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
