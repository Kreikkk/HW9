import socket
import threading
import urllib.request as urllib
import requests

from collections import Counter
from select import select
from sys import argv
from queue import Queue


SYMBOLS_TO_REMOVE = list(r"1234567890=+*|[](){}.,:;-!?$#&<>/\"'" + '\n')
LOCK = threading.Semaphore(10)

monitor = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(('localhost', 15000))
server_socket.listen()
print('Listening on http://127.0.0.1:15000')


def parse_CL():
    params = dict(map(lambda x: x.lstrip('--').split('='), argv[1:]))
    params = {k: int(v) for k, v in params.items()}

    return params


def accept(server_socket):
    client_socket, _ = server_socket.accept()
    monitor.append(client_socket)
    print('Connected client')


def retrieve_top_words(url, n):
    print(url)
    # with LOCK:
    data = urllib.urlopen(url)
    # data = requests.get(url)

    words = []
    for line in data:
        line = line.decode()
        for symb in SYMBOLS_TO_REMOVE:
            line = line.replace(symb, '')
        line = line.lower().split(' ')

        for word in line:
            if word:
                words.append(word)
            
    count = Counter(words)
    top_words = [[word, num] for word, num in sorted(count.items(), key=lambda x: x[1], reverse=True)][:n]
    top_words = dict(top_words)

    return top_words


class Worker(threading.Thread):
    def __init__(self, queue, k_top, ind):
        threading.Thread.__init__(self)
        self.k_top = k_top
        self.queue = queue
        self.ind = ind

    def run(self):
        while True:
            socket = self.queue.get()

            try:
                request = socket.recv(4096).decode()
                response = retrieve_top_words(request, self.k_top)
                print(f'Worker {self.ind} received url {request}, response {response}')
                socket.send(str(response).encode())
            except (ValueError, OSError) as e:
                # socket.close()
                # monitor.remove(socket)
                pass
                

def master():
    params = parse_CL()
    n_workers = params.get('w', 10)
    k_top = params.get('k', 1)
    queue = Queue()

    workers_pool = [Worker(queue, k_top, ind) for ind in range(n_workers)]

    for worker in workers_pool:
        worker.start()
    
    while True:
        to_read, _, _ = select(monitor, [], [])
        for socket in to_read:
            if socket is server_socket:
                accept(socket)
            else:
                queue.put(socket)


if __name__ == '__main__':
    monitor.append(server_socket)
    master()