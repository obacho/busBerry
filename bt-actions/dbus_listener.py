#!/usr/bin/python

from __future__ import absolute_import, print_function, unicode_literals

import logging
import dbus.mainloop.glib
try:
  from gi.repository import GObject as gobject
except ImportError:
  import gobject
import subprocess
from os import devnull


LOG_LEVEL = logging.INFO
LOG_FILE = "/home/pi/bt-actions/bt.log"
LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(filename=LOG_FILE, format=LOG_FORMAT, level=LOG_LEVEL)


def connect():
    logging.info('connect')
    with open(devnull, 'wb') as DEVNULL:
        subprocess.call(['aplay', '/home/pi/bt-actions/horn_once.wav'],
                        stdout=DEVNULL,
                        stderr=DEVNULL)

def disconnect():
    logging.info('disconnect')
    with open(devnull, 'wb') as DEVNULL:
        subprocess.call(['aplay', '/home/pi/bt-actions/horn_twice.wav'],
                        stdout=DEVNULL,
                        stderr=DEVNULL)

def play():
    logging.info('play')

def pause():
    logging.info('pause')

def print_event(string):
    print("\n")
    print(string)
    print('\n')

def event_handler(source, properties, *args, **kwargs):
    """
    Handles Bluez Events
    Tries to detect connection status change and playback status change
    :param source:
    :param properties:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        is_connected = properties['Connected']
        if source == 'org.bluez.MediaControl1':
            if is_connected:
                connect()
            else:
                disconnect()
    except KeyError:
        pass
    try:
        status = properties['Status']
        if status in ['paused']:
            pause()
        elif status in ['playing']:
            play()
    except KeyError:
        pass


def catchall_handler(*args, **kwargs):
    """Catch all handler.
    Catch and print information about all singals.
    """
    print('---- Caught signal ----')
    print('%s:%s\n' % (kwargs['dbus_interface'], kwargs['member']))

    print('Arguments:')
    for arg in args:
        if arg.__class__.__name__ == 'Dictionary':
            print('Dictionary:')
            for key, value in arg.items():
                print(key, ':', value)
        else:
            print ('* %s' % str(arg))
    for key, value in kwargs.items():
        print (key, ':', value)

    print("\n")
    print("\n")


if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    bus.add_signal_receiver(catchall_handler,
                            bus_name="org.bluez",
                            signal_name="PropertiesChanged",
                            interface_keyword='dbus_interface',
                            member_keyword='member'
                            )

try:
    mainloop = gobject.MainLoop()
    mainloop.run()
except KeyboardInterrupt:
    pass
