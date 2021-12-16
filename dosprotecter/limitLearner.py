class limitLearner:
    def __init__(self,normal_rate) -> None:
        self.normal_rate = normal_rate
    
    def add_report(self,rate,learning_rate):
        self.normal_rate += (rate - self.normal_rate ) * learning_rate