'''
Created on Nov 23, 2024

@author: Pat Deegan
@copyright: Copyright (C) 2024 Pat Deegan, https://psychogenic.com
'''

from ttboard.cocotb.triggers.awaitable import Awaitable
from ttboard.cocotb.clock import Clock
from ttboard.cocotb.time.value import TimeValue
from ttboard.cocotb.time.system import SystemTime
import ttboard.util.time as tm
class Timer(Awaitable):
    def __init__(self, time:int, units:str):
        super().__init__()
        self.time = TimeValue(time, units)
        
    
    def run_timer(self):
        all_clocks = Clock.all()
        # print(f"All clocks on timer: {all_clocks}")
        if all_clocks:
            fastest_clock = all_clocks[0]
            time_increment = fastest_clock.half_period
            target_time = SystemTime.current() + self.time
            increment_count = 0
            while SystemTime.current() < target_time:
                if increment_count % 1000 == 0:
                    print(f"Systime: {SystemTime.current()} (target {target_time})")
                
                increment_count += 1
                SystemTime.advance(time_increment)
        else:
            SystemTime.advance(self.time)

                
    def __iter__(self):
        return self
    
    def __next__(self): 
        self.run_timer()
        raise StopIteration
    
    
    def __await__(self):
        self.run_timer()
        yield
        return self
    