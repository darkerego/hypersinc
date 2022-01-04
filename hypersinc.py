#!/usr/bin/env python3

import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger.addHandler(logging.StreamHandler())


class HttpClient:
    headers = '''User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko)''' \
              '''Chrome/34.0.1847.131 Safari/537.36'''

    def __init__(self, verbose=False):
        if verbose:
            logger.info(f'Initialized HTTP client.')
        self.reader = None
        self.writer = None
        self.verbose = verbose

    async def open_connection(self, host, port):
        if self.verbose:
            logger.info(f'Connecting to {host}:{port}')
        self.reader, self.writer = await asyncio.open_connection(host, port)

    async def read_in_chunks(self):
        data = bytearray()
        while True:
            chunk = await self.reader.read(100)
            if not chunk:
                break
            data += chunk
        return data

    async def wait_for_data(self, message):
        await self.send_data(message)
        data = await self.read_in_chunks()
        if self.verbose:
            logger.info(f'Received: {data}')
        return data.decode()

    async def send_data(self, message):
        if self.verbose:
            logger.info(f'Sending message:\n{message} ...')
        self.writer.write(message.encode())

    async def close(self):
        if self.verbose:
            logger.info('Close the connection')
        self.writer.close()
        await self.writer.wait_closed()

    def url_parser_address(self, full_url):
        if self.verbose:
            logger.info(f'Parse address: {full_url}')
        host = full_url.split('://')[1].split('/')[0]
        try:
            host.split(':')[1]
        except IndexError:
            return host, 80
        else:
            host_port = full_url.split('://')[1].split('/')[0].split(':')
            return host_port[0], int(host_port[1])

    def url_parser_path(self, full_url):
        if self.verbose:
            logger.info(f'Parse path: {full_url}')
        res = ''
        try:
            full_url.split('://')[1].split(':')
        except IndexError:
            paths = full_url.split('://')[1].split('/')[1:]
            for p in paths:
                print(p)
                res += p + '/'
        else:
            paths = full_url.split('://')[1].split('/')[1:]
            for p in paths:
                print(p)
                res += p + '/'
        return res[:-1]

    async def http_post(self, data, full_url):
        if self.verbose:
            logger.info(f'Sending HTTP post to {full_url}\nPayload:{data}')
        host, port = self.url_parser_address(full_url)
        path = self.url_parser_path(full_url)
        http_req = "POST /%s HTTP/1.0\r\nHost: %s\r\n%s\r\nAccept: text/html\r\n" \
                   "Content-Length: %s\r\n\r\n%s" % (host, self.headers, len(data), data, path)
        return await self.wait_for_data(http_req)

    async def http_get(self, full_url):
        if self.verbose:
            logger.info(f'Sending HTTP get to {full_url}')
        host, port = self.url_parser_address(full_url)
        path = self.url_parser_path(full_url)
        http_req = "GET /%s HTTP/1.0\r\n%s\r\nHost: %s\r\nAccept: text/html\r\n\r\n" % \
                   (path, self.headers, host)
        return await self.wait_for_data(http_req)

    async def request(self, method, full_url, data=None):
        if self.verbose:
            logger.info(f'Request {method}, URL: {full_url}\nPayload:{data}')
        host, port = self.url_parser_address(full_url)
        await self.open_connection(host, port)
        if method == 'GET':
            ret = await self.http_get(full_url)
        elif method == 'POST':
            ret = await self.http_post(data, full_url)
        else:
            logger.error(f'Invalid method {method}')
            ret = False
        await self.close()
        return ret

    async def get(self, url):
        return await self.request(method='GET', full_url=url)

    async def post(self, url, data=None):
        return await self.request(method='POST', full_url=url, data=data)


async def main():
    client = HttpClient(verbose=False)
    ret = await client.request('GET', 'https://termbin.com')
    print(ret)

if __name__ == '__main__':
    asyncio.run(main())
