import ray
import time
#@ray.remote
class Counter:
    def __init__(self, init_val, sleep=True):
        # カウンターをinit_valで初期化
        self.count = init_val
        self.sleep = sleep

    def increment(self):
        if self.sleep:
            time.sleep(1)
        self.count += 1
        return self.count

    def gcount(self):
        return self.count

# 初期値0と100のカウンターを作る

#counter1, counter2 = Counter.remote(0), Counter.remote(100)
counter1 = Counter(0)
print(counter1)
s=  time.time()
#print( ray.get(counter1.count.remote()))
print(counter1.gcount())
e=  time.time()
print(e-s)
