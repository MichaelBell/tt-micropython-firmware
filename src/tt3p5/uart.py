import random

from ttboard.pins import Pins
from ttboard.demoboard import DemoBoard
import ttboard.util.time as time

from machine import Pin
from rp2 import PIO, StateMachine, asm_pio

# Set up the UART String project at a nice slow baud rate so we can see
# characters appearing
baud=150

tt = DemoBoard()
tt.shuttle.tt_um_wokwi_347144898258928211.enable()
tt.clock_project_PWM(baud)

# Initialize the project, first enable output, then transmission.
time.sleep_ms(50)
tt.in7(1)
time.sleep_ms(50)
tt.in6(1)

# Setup the UART receiver on out7
@rp2.asm_pio(autopush=True, push_thresh=8, in_shiftdir=PIO.SHIFT_RIGHT, fifo_join=rp2.PIO.JOIN_RX)
def read_prog():
    wait(0, pin, 0)
    set(x, 7).delay(22)
    label("bitloop")
    in_(pins, 1)
    jmp(x_dec, "bitloop").delay(14)
    
sm_rx = StateMachine(0, read_prog, in_base=Pin(16), freq=16*baud)
sm_rx.active(1)

# Receive and print the incoming data
byte = bytearray(1)
while True:
    sm_rx.get(byte, 24)
    print(chr(byte[0]), end="")
