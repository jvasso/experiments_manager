import string
from itertools import product
import time

alphabet = string.ascii_lowercase
i = 1

while True:
    for combination in product(alphabet, repeat=i):
        print(''.join(combination), end=', ')
        time.sleep(0.1)
    print()
    
    i += 1

