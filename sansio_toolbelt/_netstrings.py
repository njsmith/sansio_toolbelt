from ._iobuffer import IOBuffer

class NetstringConnection(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self._data = IOBuffer()

    def receive_data(self, data):
        self._data.receive_data(data)
