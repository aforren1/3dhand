import struct
import multiprocessing as mp
import numpy as np
import hid
from pylsl import (StreamInfo, StreamOutlet, StreamInlet,
                   resolve_stream, local_clock)
from psychopy.clock import monotonicClock as mt



class Hand(object):
    def __init__(self, nonblocking=False, clock=local_clock):
        self._rot = np.pi / 4.0
        self._sinrot = np.sin(self._rot)
        self._cosrot = np.cos(self._rot)
        self.nonblocking = nonblocking
        self._device = None
        self._data_buffer = np.full(15, np.nan)
        self.clock = clock

    def __enter__(self):
        self._device = hid.device()
        for d in hid.enumerate():
            if d['product_id'] == 1158 and d['usage'] == 512:
                dev_path = d['path']
        self._device.open_path(dev_path)
        self._device.set_nonblocking(self.nonblocking)
        info = StreamInfo(name='hand', type='hand', channel_count=15, nominal_srate=1000.0)
        self.outlet = StreamOutlet(info)
        return self

    def read(self):
        data = self._device.read(46)
        time = self.clock()
        if data:
            data = struct.unpack('>LhHHHHHHHHHHHHHHHHHHHH', bytearray(data))
            data = np.array(data, dtype='d')
            data[0] /= 1000.0
            data[1:] /= 65535.0
            self._data_buffer[0::3] = data[2::4] * self._cosrot - data[3::4] * self._sinrot  # x
            self._data_buffer[1::3] = data[2::4] * self._sinrot + data[3::4] * self._cosrot  # y
            self._data_buffer[2::3] = data[4::4] + data[5::4]  # z
            self.outlet.push_sample(self._data_buffer, time)
    def __exit__(self, type, value, traceback):
        self._device.close()

class LslHand(object):
    def __init__(self):
        self.flag = mp.Event()
        self.remote_ready = mp.Event()
        self.proc = None

    def __enter__(self):
        self.flag.clear()
        self.remote_ready.clear()
        self.proc = mp.Process(target=_worker, args=(self.flag, self.remote_ready))
        self.proc.daemon = True
        self.proc.start()
        self.remote_ready.wait()
        streams = resolve_stream('name', 'hand')
        self.inlet = StreamInlet(streams[0])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.inlet.close_stream()
        self.flag.set()

    def read(self):
        data, timestamps = self.inlet.pull_chunk()
        if timestamps:
            return data, timestamps
        return None, None


def _worker(flag, remote_ready):
    dev = Hand(nonblocking=False, clock=mt.getTime)
    with dev as d:
        remote_ready.set()
        while not flag.is_set():
            d.read()
