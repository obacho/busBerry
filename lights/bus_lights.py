#!/usr/bin/env python

import sys
import os
import signal
import logging
import dbus
import dbus.service
import dbus.mainloop.glib
import RPi.GPIO as GPIO
from time import sleep
import threading
try:
  from gi.repository import GObject as gobject
except ImportError:
  import gobject

# very important: keeps threads running in background
# and that's exactly what we need for the blinking
gobject.threads_init()


# GPIO_stuff
# use gpio pin numbering
GPIO.setmode(GPIO.BCM)
front       = 19
front_left  = 16
front_right = 26
back_left   = 21
back_right  = 20
left_indicators = [front_left, back_left]
right_indicators = [front_right, back_right]
indicators = [front_left, back_left, front_right, back_right]
# select GPIO
GPIO.setup(front, GPIO.OUT, initial=0)
GPIO.setup(front_left, GPIO.OUT, initial=0)
GPIO.setup(front_right, GPIO.OUT, initial=0)
GPIO.setup(back_right, GPIO.OUT, initial=0)
GPIO.setup(back_left, GPIO.OUT, initial=0)
stop_indicating_event = threading.Event()
stop_light_event = {front: threading.Event(),
                    front_left: threading.Event(),
                    front_right: threading.Event(),
                    back_left: threading.Event(),
                    back_right: threading.Event()}

def print_threads():
    # prints all active threads
    active_threads = threading.enumerate()
    threads = ""
    for thread in active_threads:
        threads += " " + thread.name
    print "active threads: {}".format(threads)

def led_on_thread(stop_event, id, brightness=1.0):
    """
       method to be run as thread to control led brightness
       by quickly switching on and off
    """
    if brightness == 1.0:
        on_time = 0.1
        off_time = 0
    elif brightness == 0:
        on_time = 0
        off_time = 0.1
    else:
        on_time == brightness*0.001
        off_time == 0.001
    while not stop_event:
        GPIO.output(id, True)
        sleep(on_time)
        GPIO.output(id, False)
        event_is_set = stop_event.wait(off_time)
    GPIO.output(id, False)

def led_on(id, brightness=1.0):
    """
       Turns on a LED
       to chosen brightness (between 0 and 1)
    """
    stop_light_event[id].set()
    thread = threading.Thread(name="light_{}".format(id),
                              target=led_on_thread,
                              args=(stop_light_event[id],
                                    id,
                                    brightness))
    thread.start()

def led_off(id):
    """
       Turns off an LED
    """
    stop_light_event[id].clear()

def lights_on():
    GPIO.output(front, 1)
    GPIO.output(back_left, 1)
    GPIO.output(back_right, 1)

def lights_off():
    GPIO.output(front, 0)
    GPIO.output(back_left, 0)
    GPIO.output(back_right, 0)
#    led_off(front)
#    led_off(back_left)
#    led_off(back_right)

def all_lights_off():
    stop_indicating_event.set()
    sleep(0.5)
    GPIO.output(front, 0)
    GPIO.output(front_left, 0)
    GPIO.output(front_right, 0)
    GPIO.output(back_left, 0)
    GPIO.output(back_right, 0)
#    led_off(front)
#    led_off(back_left)
#    led_off(back_right)
#    led_off(front_left)
#    led_off(front_right)

def leftright():
    state_back_left, state_back_right = GPIO.input(back_left), GPIO.input(back_right)
    GPIO.outpt(left_indicators, 1)
    sleep(.25)
    GPIO.output(left_indicators, 0)
    GPIO.output(right_indicators, 1)
    sleep(.25)
    GPIO.output(right_indicators,0)
    GPIO.output(back_left, state_back_left)
    GPIO.output(back_right, state_back_right)

def indicate(n_times=1, pattern=['all']):
    state_back_left, state_back_right = GPIO.input(back_left), GPIO.input(back_right)
    GPIO.output(indicators, 0)

    if pattern == 'leftright':
        def run_pattern():
            GPIO.output(left_indicators, 1)
            sleep(.25)
            GPIO.output(left_indicators, 0)
            GPIO.output(right_indicators, 1)
            sleep(.25)
            GPIO.output(right_indicators, 0)
    else:
        def run_pattern():
            GPIO.output(indicators, 1)
            sleep(0.5)
            GPIO.output(indicators, 0)
            sleep(0.5)
    for i in range(n_times):
        run_pattern()

    GPIO.output(back_left, state_back_left)
    GPIO.output(back_right, state_back_right)


def indicate_method(stop_indicating_event):
    bl_state = GPIO.input(back_left)
    br_state = GPIO.input(back_right)
    while not stop_indicating_event.isSet():
	#for indi_id in indicators:
        #    led_on(indi_id)
        GPIO.output(indicators, 1)
        sleep(0.5)
	#for indi_id in indicators:
        #    led_off(indi_id)
        GPIO.output(indicators, 0)
        event_is_set = stop_indicating_event.wait(0.5)
    GPIO.output([front_left, front_right], False)
    GPIO.output(back_left, bl_state)
    GPIO.output(back_right, br_state)

def start_indicate():
    stop_indicating_event.clear()
    thread_names = [x.name for x in threading.enumerate()]
    if not "indicate" in thread_names:
        indicating_thread = threading.Thread(name="indicate",
                                             target=indicate_method,
                                             args=(stop_indicating_event,))
        indicating_thread.start()

def stop_indicate():
    stop_indicating_event.set()


