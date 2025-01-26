from contextlib import contextmanager
from queue import Queue
import pyodbc

class ConnectionPool:
    def __init__(self, conn_str, pool_size=5):
        self.conn_str = conn_str
        self.pool = Queue(maxsize=pool_size)
        for _ in range(pool_size):
            self.pool.put(self._create_connection())

    def _create_connection(self):
        return pyodbc.connect(self.conn_str, timeout=30)

    @contextmanager
    def get_connection(self):
        connection = self.pool.get()
        try:
            yield connection
        finally:
            self.pool.put(connection)