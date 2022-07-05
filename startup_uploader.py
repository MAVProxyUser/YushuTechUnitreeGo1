"""Unitree Uploader
needs python3

get: return the list of uploaded packages in json
post: post package to the upload folder

author: Zhongkai Chen
site: www.unitree.com
"""

import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import html
import shutil
import mimetypes
import re
from io import BytesIO


class UnitreeUpdateManager(http.server.BaseHTTPRequestHandler):
    file_list = '{"files":[]}'
    def do_GET(self):
        """Serve a GET request."""
        f = self.send_head()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_POST(self):
        """Serve a POST request."""
        r, info = self.deal_post_data()
        f = BytesIO()
        f.write(("{'info':'"+info+"'}").encode())
        length = f.tell()
        f.seek(0)
        if r:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin","*")
        else:
            self.send_response(400)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            self.copyfile(f, self.wfile)
            f.close()

    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")


        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(
            r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        ext = os.path.splitext(fn[0])[1]
        if ext != '.zip':
            return (False, "File ext not supported")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                self.list_directory(path)
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        self.list_directory(path)
        return (False, "Unexpect Ends of data.")

    def send_head(self):
        path = self.translate_path(self.path)
        print(path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/upload/'):
                self.send_response(301)
                self.send_header("Access-Control-Allow-Origin","*")
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.list_directory(path)
                f = BytesIO()
                f.write(self.file_list.encode())
                length = f.tell()
                f.seek(0)
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin","*")
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(length))
                self.end_headers()
                return f
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, '{"info":"No Permission"}')
            return None
        list.sort(key=lambda a: a.lower())
        self.file_list = '{"files":['
        length = len(list)
        for i, name in enumerate(list):
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            if(i +1 < length):
                self.file_list = self.file_list + ('{"name":"%s","link":"%s"},' % (html.escape(linkname), html.escape(path+"/"+linkname)))               
            else: 
                self.file_list = self.file_list + ('{"name":"%s","link":"%s"}' % (html.escape(linkname), html.escape(path+"/"+linkname)))     
        self.file_list = self.file_list + ']}'
    

    def translate_path(self, path):
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path

    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })


if __name__ == '__main__':
    server_address = ('', 9800)
    httpd = http.server.HTTPServer(server_address,UnitreeUpdateManager)
    httpd.serve_forever()
