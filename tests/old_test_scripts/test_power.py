from jtop import jtop
from time import sleep
import numpy as np

def measure():
    jetson = jtop()
    pow = list()
    jetson.attach(lambda jet : pow.append((jet.power['tot']['power'] / 1000)))

    print("Starting measurement")
    jetson.start()
    sleep(60)
    jetson.close()
    print("Ending measurement")
    return pow


pow_list = measure()
print("Power:")
print(pow_list)
print(np.mean(pow_list))
