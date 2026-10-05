# nmea data flow handling
# author: Łukasz Stolzmann

import os
import signal
import datetime
import threading
import init_params
import multiprocessing
from queue import Queue
from ship_handling import Director
from data_source import LazySocketConn, SerialInput, CollzoneDatabaseConnection

class NMEADataStream:
    @classmethod
    def from_server(cls, addr, port, destination):
        return cls(LazySocketConn(addr, port), destination)
    
    @classmethod
    def from_serial(cls, port, baudrate, destination):
        return cls(SerialInput(port, baudrate), destination)

    def __init__(self, source, destination):
        self._sentinel = object()
        self._queue = Queue()
        self._director = Director.create(destination)
        self._source = source
        self._connected = True

        self._log_filename = 'log_file.txt'

    def run(self):
        self._threads = threading.Thread(target=self._producer), threading.Thread(target=self._consumer)
        for th in self._threads:
            th.start()

    def terminate(self):
        self._connected = False
        for th in self._threads:
            th.join()

    def _producer(self):
        with self._source as src:
            while self._connected:
                self._queue.put(src.readline())
            self._queue.put(self._sentinel)

    def _consumer(self):
        while True:
            recv_data = self._queue.get()
            
            with open(self._log_filename, 'a') as f:
                print(recv_data, file=f, end='')
            if recv_data is self._sentinel:
                self._queue.put(self._sentinel)
                print(f'{self.__class__.__name__} terminated.')
                break
            self._director.decide(recv_data)

class DatabaseConsumer(multiprocessing.Process):
    def __init__(self, task_q, result_q):
        multiprocessing.Process.__init__(self)
        self._task_q = task_q
        self._result_q = result_q
        self._db_connection = CollzoneDatabaseConnection(init_params.CONNECTION_NAME)

    def run(self):
        proc_name = self.name
        while True:
            next_task = self._task_q.get()
            if next_task is None:
                print(f'Exiting {proc_name}')
                self._task_q.task_done()
                break
            print(f'Processing COLLZONE query...: {next_task}')
            with self._db_connection as cursor:
                answer = next_task(cursor)
            self._task_q.task_done()
            self._result_q.put(answer)
        return

                

                

        