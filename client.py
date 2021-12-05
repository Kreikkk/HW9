import socket
import threading
from queue import Queue

from sys import argv

TCP_IP = '127.0.0.1'
TCP_PORT = 15000
BUFFER_SIZE = 4096


def parse_file(filename):
    with open(filename, 'r') as f:
        urls = f.readlines()
    urls = [url.replace('\n', '') for url in urls]

    return urls


def parse_CL():
    params = dict(map(lambda x: x.lstrip('--').split('='), argv[1:]))
    params = {k: int(v) for k, v in params.items()}

    return params

def master():
    skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.connect((TCP_IP, TCP_PORT))
    params = parse_CL()
    n_workers = params.get('w', 10)
    url_fname = params.get('f', 'urls.txt')
    urls = parse_file(url_fname)
    queue = Queue()

    workers_pool = [Worker(queue, skt, ind) for ind in range(n_workers)]
    for worker in workers_pool:
            worker.start()
    
    for url in urls:
        print(f'Adding {url}')
        queue.put(url)

    for worker in workers_pool:
            worker.join()


class Worker(threading.Thread):
    def __init__(self, queue, skt, ind):
        threading.Thread.__init__(self)
        self.socket = skt
        self.queue = queue
        self.ind = ind

    def run(self):
        while True:
            url = self.queue.get().encode()
            self.socket.send(url)
            response = self.socket.recv(4096).decode()
            print(f'Worker {self.ind} sent {url}, received {response}')


if __name__ == '__main__':
    master()