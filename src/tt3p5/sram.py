import random

from ttboard.pins import Pins
from ttboard.demoboard import DemoBoard
import ttboard.util.time as time

class SRAM:
    def __init__(self, pins:Pins):
        self.p = pins 
        self._data_in_write = 0
        
        for p in self.p.bidirs:
            p.mode = Pins.OUT 
            
        self.p.input_byte = 0
        self.p.bidir_byte = 0
        
    @property 
    def bank_select(self):
        return self.p.in6()
    
    @bank_select.setter 
    def bank_select(self, v:int):
        self.p.in6(v)
        
    @property 
    def we(self):
        return self.p.in7()
    
    @we.setter 
    def we(self, v:int):
        if v:
            self.p.in7(1)
        else:
            self.p.in7(0) 
        
    @property 
    def addr_low(self):
        return self.p.input_byte & 0x3f
    
    @addr_low.setter 
    def addr_low(self, v:int):
        self.p.input_byte = (self.p.input_byte & ~0x3f) | (v & 0x3f)
        
    @property 
    def addr_high_in(self):
        return self.p.bidir_byte & 0x1f
    
    @addr_high_in.setter 
    def addr_high_in(self, v:int):
        self.p.bidir_byte = (self.p.bidir_byte & ~0x1f) | (v & 0x1f)
        
    @property 
    def data_out(self):
        return self.p.output_byte
    
    @property 
    def data_in(self):
        return self.p.bidir_byte
    
    @data_in.setter
    def data_in(self, v:int):
        self.p.bidir_byte = v        
    
        
        
def setup():
    tt = DemoBoard()
    
    tt.shuttle.tt_um_urish_sram_poc.enable()

    sram = SRAM(tt.pins)
    
    tt.reset_project(True)
    tt.clock_project_PWM(1e4)
    time.sleep_ms(1)
    
    tt.reset_project(False)
    time.sleep_ms(1)
    return tt, sram

def test():
    tt, sram = setup()
    tt.clock_project_stop()
    
    # Outputs only valid when clock is low, so start clock low
    tt.project_clk.off()
    
    offset = random.randint(0, 192)

    # Note that the bank select doesn't work, so we cna only use the bottom 64 bytes
    print("Writing RAM")
    sram.we = 1
    for i in range(0,64):
        sram.addr_low = i
        sram.data_in = i + offset
        tt.clock_project_once()
                
    print('Reading RAM')
    sram.we = 0
    for i in range(0,64):
        sram.addr_low = i 
        
        tt.clock_project_once()
        
        if sram.data_out != i + offset:
            print(f"Error at {i}: {sram.data_out} != {i}")
        
    print('Verify random reads and writes')
    ram = [i + offset for i in range(64)]
    for i in range(1000):
        addr = random.randint(0, 63)
        sram.addr_low = addr

        if random.randint(0, 1) == 1:
            data = random.randint(0, 255)
            ram[addr] = data
            sram.data_in = data
            sram.we = 1
            tt.clock_project_once()
            sram.we = 0
        else:
            tt.clock_project_once()
            if sram.data_out != ram[addr]:
                print(f"Error at {addr}: {sram.data_out} != {ram[addr]}")
        
    print('Verify RAM contents')
    for i in range(0,64):
        sram.addr_low = i
        tt.clock_project_once()
        if sram.data_out != ram[i]:
            print(f"Error at {i}: {sram.data_out} != {ram[i]}")
        
    print("Test done")
    return tt, sram
    
if __name__ == "__main__":
    tt, dffram = test()
