# -*- coding: utf-8 -*-
"""
Copyright (c) 2021, Eisenberger Tamás.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Sep 3, 2021

@author: u-foka
"""
import os
import sys
import traceback
import socket
from atom.atom import set_default
from atom.api import Value, Instance, Str, Int
from inkcut.core.api import Plugin, Model, log
from inkcut.device.plugin import DeviceTransport
from twisted.internet import reactor, stdio
from twisted.internet.protocol import Protocol, connectionDone

from inkcut.device.transports.raw.plugin import RawFdProtocol


class TcpFdConfig(Model):
    host = Str().tag(config=True)
    port = Int(9100).tag(config=True)

class TcpFdTransport(DeviceTransport):

    #: Default config
    config = Instance(TcpFdConfig, ()).tag(config=True)

    # Store endpoint for logging
    endpoint = Str()

    # Socket handle
    sock = Value()

    #: Wrapper
    _protocol = Instance(RawFdProtocol)

    def connect(self):
        config = self.config
        endpoint = self.endpoint = config.host + ":" + str(config.port);
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((config.host, config.port))
            log.debug("-- {} | opened".format(endpoint))
            self._protocol = RawFdProtocol(self, self.protocol)
            self.connected = True
        except Exception as e:
            #: Make sure to log any issues as these tracebacks can get
            #: squashed by twisted
            log.error("{} | {}".format(endpoint, traceback.format_exc()))
            raise

    def write(self, data):
        if not self.sock:
            raise IOError("{} is not opened".format(self.device_path))
        log.debug("-> {} | {}".format(self.endpoint, data))
        if hasattr(data, 'encode'):
            data = data.encode()
        self.last_write = data
        self.sock.sendall(data)

    def disconnect(self):
        if self.sock:
            log.debug("-- {} | closed by request".format(self.endpoint))
            self.sock.close();
            self.sock = None
            self.connected = False

    def __repr__(self):
        return self.endpoint

