import socket
import threading
from queue import Queue
from time import time

from tools import parse_CL, parse_file


TCP_IP = '127.0.0.1'
TCP_PORT = 15000


def master():
    params = parse_CL()
    n_workers = int(params.get('w', 10))
    url_fname = params.get('f', 'urls.txt')
    urls = parse_file(url_fname)
    queue = Queue()

    t1 = time()
    workers_pool = [Worker(queue, ind) for ind in range(n_workers)]
    
    for url in urls:
        queue.put(url)
    
    for worker in workers_pool:
        worker.start()

    for worker in workers_pool:
            worker.join()
    print(f'Time = {time() - t1}')


class Worker(threading.Thread):
    def __init__(self, queue, ind):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((TCP_IP, TCP_PORT))
        self.queue = queue
        self.ind = ind

    def run(self):
        while True:
            if self.queue.empty():
                break
            
            url = self.queue.get()
            self.socket.send(url.encode())
            response = self.socket.recv(4096).decode()
            print(f'Worker {self.ind} sent {url}, received {response}')


if __name__ == '__main__':
    master()