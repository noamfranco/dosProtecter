import time
from dosprotecter.constants import *
class rateCounter:
    def __init__(self,time_frame) -> None:
        self.lst1 = [0] * TIME_FRAME
        self.total_events = 0
        self.index_time = time.time()
        self.index = 0
        self.start_time = time.time()
        self.time_frame = time_frame

    def clean_cell(self,i):
        self.total_events -= self.lst1[i]
        print(self.lst1[i])
        self.lst1[i] = 0
    
    def add_cell(self,i,num_events):
        self.lst1[i] += num_events
        self.total_events += num_events
    
    def add_event(self):
        time_report = time.time()
        
        if self.index_time + self.time_frame < time.time():
            self.lst1 = [0] * self.time_frame
        
        index1 = (int(time_report) % self.time_frame)
        index2 = (self.index) % self.time_frame
        if index1 < self.index:
            v = index1 + (self.time_frame - self.index)
        else:
            v = index1 - self.index
        for k in range(v):
            index2 += 1
            index2 = index2 % self.time_frame
            self.clean_cell(index2)
            
        
        self.add_cell(index2,1)
        self.index = index2
        self.index_time = max(time_report,self.index_time)
        return self.total_events

def test():
    rate = rateCounter()
    for i in range(60):
        rate.add_event()
        print(rate.lst1)
        time.sleep(0.5)
    for i in range(30):
        rate.add_event()
        print(rate.lst1)
        time.sleep(1)

if __name__ == "__main__":
    test()