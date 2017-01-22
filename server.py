#  coding: utf-8 
import SocketServer
import socket
import os
import sys
import mimetypes
from time import gmtime, strftime

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

http_response = { 200: "HTTP/1.1 200 OK",
                  302: "HTTP/1.1 302 Found",
                  404: "HTTP/1.1 404 Not Found",
                  405: "HTTP/1.1 405 Method Not Allowed" }

class MyWebServer(SocketServer.BaseRequestHandler):

    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        # By Vijay Dev (https://stackoverflow.com/users/27474/vijay-dev) on stackoverflow:
        # https://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
        self.date = strftime("%a, %d %b %Y %X GMT", gmtime()) 
        self.path = "./www"
        print ("Got a request of: %s\n" % self.data)

        if self.verify_method():
            self.verify_path() 
        self.send_response()

        
    def verify_method(self):
        self.method = self.data.split()[0]        
        if self.method == "GET":
            return True
      
        self.code = 405
        return False
    
    def verify_path(self):
        self.path += self.data.split()[1]
        print "PATH: " + self.path

        if self.verify_path_depth() == False:
            self.code = 404
            return
        
        if self.path.endswith("/"):
            self.path += "index.html"
        
        if not (self.path.endswith(".html") or self.path.endswith(".css" )) :
            try:
                print "PATHHHHHH:" + self.path + "/index.html"
                self.content = open(self.path + "/index.html", 'r').read()
                self.code = 302
                self.path = self.path[5:] + "/"
                return
            except:
                self.code = 404
                return
      
        try:
            self.content = open(self.path, 'r').read()
            self.mimetype = mimetypes.guess_type(self.path)[0]
            # By rajasaur (https://stackoverflow.com/users/56465/rajasaur)
            # on stackoverflow: https://stackoverflow.com/questions/6591931/getting-file-size-in-python
            self.content_size = os.path.getsize(self.path) 
            self.code = 200
                
        except:
            self.code = 404

    # By OpenStack Vulnerability Management Team
    # on openstack: https://security.openstack.org/guidelines/dg_using-file-paths.html
    def verify_path_depth(self):
        base_directory = os.getcwd() + "/www"
        print "BASE DIRECTORY", base_directory
        print "REAL PATH: " + os.path.realpath(self.path)
        print "RETURN REAL PATH: ", os.path.realpath(self.path).startswith(base_directory)
        print "ABS PATH: " +  os.path.abspath(self.path)
        print "RETURN ABS PATH: ", os.path.abspath(self.path).startswith(base_directory)
    
        return os.path.realpath(self.path).startswith(base_directory)

        
            
    def send_response(self):
        if self.code == 405:
            self.request.sendall( http_response[405]  + "\r\n",
                                  "Allow: GET"  + "\r\n")
            print(http_response[405] + "\r\n")
            
        elif self.code == 200:
            self.request.sendall( http_response[200] + "\r\n" +
                                  "Content-Type: " + self.mimetype + "; charset=UTF-8" + "\r\n" + 
                                  "Date: " + self.date + "\r\n" +
                                  "Content-Length: " + str(self.content_size)  + "\r\n" +
                                  "\r\n" +
                                  self.content + "\r\n")

            print( http_response[200] + "\r\n" +
                   "Content-Type: " + self.mimetype + "; charset=UTF-8" + "\r\n" +
                   "Date: " + self.date + "\r\n" +
                   "Content-Length: " + str(self.content_size)  + "\r\n" +
                   "\r\n" +
                   self.content + "\r\n")

        elif self.code == 404:
            self.request.sendall(http_response[404]  + "\r\n")
            print(http_response[404] + "\r\n")

        elif self.code == 302:
            self.request.sendall( http_response[302]  + "\r\n"
                                  "Date: " + self.date + "\r\n" +
                                  "Location: " + self.path + "\r\n")
            print( http_response[302] + "\r\n"
                   "Date: " + self.date + "\r\n" +
                   "Location: " + self.path + "\r\n")
            

            
if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8080
    SocketServer.TCPServer.allow_reuse_address = True
    
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

