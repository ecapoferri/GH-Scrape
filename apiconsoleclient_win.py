import requests
from os import system
from sys import argv
from time import sleep
from datetime import datetime
now = datetime.now
import logging

# $python apiconsoleclient.py <lines> <refersh time sec> <api url>

# refresh time
while True:
    try:
        wait = int(argv[2])
        limit: int = 0 - abs(int(argv[1]))
        resp = requests.get(
            argv[3])
        jsdata: dict = resp.json()

        system('cls')
        # one timestamp at the top of the refresh
        print(now().strftime(f"%X"))
        print(f"========")
        # -1 stop slice cuts the extra newline
        for i, m in enumerate(jsdata.values()):
            l = len(jsdata.values())
            # print only lines in the desired range
            if i > l + limit: print(f"{m[:-1]}")
            # countdown
        print(f"========")
        for j in range(wait):
            counter = f">> {wait-j} <<"
            print(f"\t{counter:^80}\r", end='')
            sleep(1)

    except KeyboardInterrupt:
        logging.error("KeyboardInterrupt! Ok, byeeeee!")
        break
