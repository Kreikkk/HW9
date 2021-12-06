import socket
import threading
import requests
import urllib.request as urllib

from collections import Counter
from select import select
from sys import argv
from queue import Queue


SYMBOLS_TO_REMOVE = list(r"1234567890=+*|[](){}.,:;-!?$%#&<>/\"'" + '\n')
LOCK = threading.Lock()

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


def retrieve_top_words(url, n):
    data = requests.get(url)

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


def master():
    queue = Queue()
    params = parse_CL()
    n_workers = params.get('w', 10)
    k_top = params.get('k', 1)
    global verbose
    global urls_fetched
    verbose = params.get('v', 0)
    urls_fetched = 0

    workers_pool = [threading.Thread(target=fetch, args=(queue, k_top, i)) for i in range(n_workers)]

    for worker in workers_pool:
        worker.start()
    
    while True:
        to_read, _, _ = select(monitor, [], [])
        for socket in to_read:
            if socket is server_socket:
                accept(socket)
            else:
                url = socket.recv(4096).decode()
                if not url:
                    continue
                queue.put((url, socket))


def fetch(queue, k_top, ind):
    while True:
        url, socket = queue.get()
        try:
            response = retrieve_top_words(url, k_top)
            print(f'Worker {ind} received url {url}, response {response}')
            socket.send(str(response).encode())

            with LOCK:
                global urls_fetched
                urls_fetched += 1
            global verbose
            if verbose:
                print(f'URLs fetched: {urls_fetched}')
        except (ValueError, OSError) as e:
            break


if __name__ == '__main__':
    monitor.append(server_socket)
    master()