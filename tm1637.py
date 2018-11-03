#!/usr/bin/env python3

import subprocess
from time import time, sleep, localtime

from wiringpi2 import wiringPiSetupGpio, pinMode, digitalRead, digitalWrite, GPIO
wiringPiSetupGpio()

CLK = 21
DIO = 20

"""
      A
     ---
  F |   | B
     -G-
  E |   | C
     ---
      D

"""


class TM1637:
    I2C_COMM1 = 0x40
    I2C_COMM2 = 0xC0
    I2C_COMM3 = 0x80
    digit_to_segment = [
        0b0111111, # 0
        0b0000110, # 1
        0b1011011, # 2
        0b1001111, # 3
        0b1100110, # 4
        0b1101101, # 5
        0b1111101, # 6
        0b0000111, # 7
        0b1111111, # 8
        0b1101111, # 9
        0b1110111, # A
        0b1111100, # b
        0b0111001, # C
        0b1011110, # d
        0b1111001, # E
        0b1110001  # F
        ]
     # For flipped display
     digit_to_segment1 = [
         #GFEDCBA    
        0b0111111, # 0
        0b0110000, # 1
        0b1011011, # 2
        0b1111001, # 3
        0b1110100, # 4
        0b1101101, # 5
        0b1101111, # 6
        0b0111000, # 7
        0b1111111, # 8
        0b1111101, # 9
        0b1111110, # A
        0b1100111, # b
        0b0001111, # C
        0b1110011, # d
        0b1001111, # E
        0b1001110  # F
        ]    
 

    def __init__(self, clk, dio):
        self.clk = clk
        self.dio = dio
        self.brightness = 0x0f

        pinMode(self.clk, GPIO.INPUT)
        pinMode(self.dio, GPIO.INPUT)
        digitalWrite(self.clk, GPIO.LOW)
        digitalWrite(self.dio, GPIO.LOW)

    def bit_delay(self):
        sleep(0.001)
        return
   
    def set_segments(self, segments, pos=0):
        # Write COMM1
        self.start()
        self.write_byte(self.I2C_COMM1)
        self.stop()

        # Write COMM2 + first digit address
        self.start()
        self.write_byte(self.I2C_COMM2 + pos)

        for seg in segments:
            self.write_byte(seg)
        self.stop()

        # Write COMM3 + brightness
        self.start()
        self.write_byte(self.I2C_COMM3 + self.brightness)
        self.stop()

    def start(self):
        pinMode(self.dio, GPIO.OUTPUT)
        self.bit_delay()
   
    def stop(self):
        pinMode(self.dio, GPIO.OUTPUT)
        self.bit_delay()
        pinMode(self.clk, GPIO.INPUT)
        self.bit_delay()
        pinMode(self.dio, GPIO.INPUT)
        self.bit_delay()
  
    def write_byte(self, b):
      # 8 Data Bits
        for i in range(8):

            # CLK low
            pinMode(self.clk, GPIO.OUTPUT)
            self.bit_delay()

            pinMode(self.dio, GPIO.INPUT if b & 1 else GPIO.OUTPUT)

            self.bit_delay()

            pinMode(self.clk, GPIO.INPUT)
            self.bit_delay()
            b >>= 1
      
        pinMode(self.clk, GPIO.OUTPUT)
        self.bit_delay()
        pinMode(self.clk, GPIO.INPUT)
        self.bit_delay()
        pinMode(self.clk, GPIO.OUTPUT)
        self.bit_delay()

        return



def show_clock(tm):
        t = localtime()
        sleep(1 - time() % 1)
        d0 = tm.digit_to_segment[t.tm_hour // 10] if t.tm_hour // 10 else 0
        d1 = tm.digit_to_segment[t.tm_hour % 10]
        d2 = tm.digit_to_segment[t.tm_min // 10]
        d3 = tm.digit_to_segment[t.tm_min % 10]
        tm.set_segments([d0, 0x80 + d1, d2, d3])
        sleep(.5)
        tm.set_segments([d0, d1, d2, d3])
            
def show_clock_flipped(tm):
        t = localtime()
        sleep(1 - time() % 1)
        d0 = tm.digit_to_segment1[t.tm_hour // 10] if t.tm_hour // 10 else 0
        d1 = tm.digit_to_segment1[t.tm_hour % 10]
        d2 = tm.digit_to_segment1[t.tm_min // 10]
        d3 = tm.digit_to_segment1[t.tm_min % 10]
        tm.set_segments([d3, 0x80 + d2, d1, d0])
        sleep(.5)
        tm.set_segments([d3, d2, d1, d0])

if __name__ == "__main__":
    tm = TM1637(CLK, DIO)


    while True:
        show_clock_flipped(tm)



