from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from dosprotector import Dosprotector
dp = Dosprotector(5)
class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.0'
  
    def do_GET(self, body=True):
        try:
            ip = self.client_address[0]
            print(ip)
            dp.add_report(ip)
            if ip in dp.in_quarantine:
                msg = "You sent too many requests MF"
                self.send_response(443, msg)
                self.end_headers()
                
                if body:
                    self.wfile.write(msg.encode(encoding='UTF-8',errors='strict'))
                return
            # Parse request
            hostname = 'text.npr.org'
            url = 'https://{}{}'.format(hostname, self.path)
            req_header = self.parse_headers()

            # Call the target service
            resp = requests.get(url, headers=req_header, verify=False)

            # Respond with the requested data
            self.send_response(resp.status_code)
            self.send_resp_headers(resp)
            msg = resp.text
            if body:
                self.wfile.write(msg.encode(encoding='UTF-8',errors='strict'))
            return
        finally:
            self.finish()

    
    def parse_headers(self):
        req_header = {}
        for line in self.headers:
            line_parts = [o.strip() for o in line.split(':', 1)]
            if len(line_parts) == 2:
                req_header[line_parts[0]] = line_parts[1]
        return self.inject_auth(req_header)
    
    def inject_auth(self, headers):
        headers['Authorizaion'] = 'Bearer secret'
        return headers
    
    def send_resp_headers(self, resp):
        respheaders = resp.headers
        print ('Response Header')
        for key in respheaders:
            if key not in ['Content-Encoding', 'Transfer-Encoding', 'content-encoding', 'transfer-encoding', 'content-length', 'Content-Length']:
                print (key, respheaders[key])
                self.send_header(key, respheaders[key])
        self.send_header('Content-Length', len(resp.content))
        self.end_headers()

if __name__ == '__main__':
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    print('http server is running')
    httpd.serve_forever()
