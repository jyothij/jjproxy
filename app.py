from http.server import BaseHTTPRequestHandler, HTTPServer
import time
# import asyncio
import jwt
import random
import requests
import os
from io import StringIO
import logging

secret = os.getenv('SECRET', 'a9ddbcaba8c0ac1a0a812dc0c2f08514b23f2db0a68343cb8'
                   '199ebb38a6d91e4ebfb378e22ad39c2d01d0b4ec9c34aa91056862ddace'
                   '3fbbd6852ee60c36acbf')
# hostTarget = 'https://reqres.in'
hostTarget = os.getenv('TARGETURL', 'https://postman-echo.com/post')
requestCount = 0
timeStart = 0


def getJwt():
    global secret
    epochTime = time.time()
    # Claims
    iat = int(epochTime)
    todaysDate = time.strftime('%m/%d/%Y', time.localtime(epochTime))
    # Nonce as generated by python-oauth2, length = 20
    jti = ''.join([str(random.randint(0, 9)) for i in range(20)])
    payload = {'user': 'username', 'date': todaysDate, 'iat': iat, 'jti': jti}
    return jwt.encode(payload, secret, algorithm='HS512')


class ProxyHandler(BaseHTTPRequestHandler):
    protocolVersion = 'HTTP/1.0'

    # Copy all headers from the incoming request
    # And Remove Content Length to override later on
    def createHeaders(self):
        reqHeader = {}
        for header in self.headers:
            if not header.upper() == 'Content-Length'.upper():
                reqHeader[header] = self.headers[header]
        reqHeader['x-my-jwt'] = getJwt()
        return reqHeader

    def do_GET(self, body=True):
        global requestCount
        global timeStart
        requestCount += 1
        try:
            try:
                sio = StringIO()
                logging.info(f'Received GET request at {time.time()}')
                logging.debug(f'{type(self.path)}')
                if self.path == '/status':
                    logging.info('Got status request')
                    timeUp = int(time.time() - timeStart)
                    sio.write('<html><head><title>Proxy Status</title></head>')
                    sio.write('<body><h1>Proxy Status</h1>')
                    sio.write(f'<li>Time from Start: {timeUp} (s)</li>')
                    sio.write(f'<li>Number of Requests Processed: {requestCount}</li>')
                    sio.write('</body></html>')
                else:
                    sio.write('Nothing to report')
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(sio.getvalue())))
                self.end_headers()
                self.wfile.write(bytes(sio.getvalue(), 'utf-8'))
                return
            finally:
                logging.info(f'Processed GET request at {time.time()}')
                sio.close()
        except Exception as e:
            self.send_error(500, f'{type(e)} error')
            logging.error(str(e))

    def do_POST(self):
        global requestCount
        requestCount += 1
        try:
            logging.info(f'Received POST request at {time.time()}')
            contentLength = int(self.headers['Content-Length'])
            body = self.rfile.read(contentLength)
            host = hostTarget
            url = f'{host}{self.path}'
            reqHeaders = self.createHeaders()
            logging.info(f'request to URL={url}, data={body}, headers={reqHeaders}')
            response = requests.post(url=url, headers=reqHeaders, data=body, verify=False)
            logging.info(f'response status code={response.status_code}')
            self.send_response(response.status_code)
            rc = response.content
            length = len(rc)
            logging.info(f'response content ={rc}, {length}')
            for header in reqHeaders:
                self.send_header(header, reqHeaders[header])
            self.send_header('Content-Length', length)
            self.end_headers()
            self.wfile.write(rc)
            logging.info(f'Sent POST response back request at {time.time()}')
        except Exception as e:
            self.send_error(500, f'{type(e)} error')
            logging.error(str(e))
        finally:
            logging.info(f'Processed POST request at {time.time()}')


def main():
    global timeStart
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('HTTP_PORT', 8081))
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    try:
        httpServer = HTTPServer((host, port), ProxyHandler)
        timeStart = time.time()
        logging.info(f'Started HTTP Server v1 {host}:{port} at {time.asctime()}')
        logging.info(f'TARGETURL={hostTarget}, SECRET={secret}')
        httpServer.serve_forever()
    except KeyboardInterrupt:
        pass
    logging.info(f'Shutting HTTP Server {host}:{port}')
    httpServer.server_close()


if __name__ == '__main__':
    main()
