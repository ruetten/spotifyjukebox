import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

class Serv(http.server.SimpleHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        try:
            f = open(self.path[1:])
            file_to_open = f.read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))
        try:
            f.close()
        except:
            pass

httpd = socketserver.TCPServer(("", PORT), Serv)
httpd.serve_forever()