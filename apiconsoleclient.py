import logging
from tqdm import tqdm
import requests
from os import system, get_terminal_size
from sys import argv
from time import sleep
from datetime import datetime
now = datetime.now

# $python apiconsoleclient.py <lines> <refersh time sec> <api url>
def border(strng: str) -> str:
	return strng.center(w, '=')

bar_format='REFRESH IN: {remaining_s:.0f} s |{bar}| (** ^C to EXIT **)'

# refresh time
while True:
	try:
		w = get_terminal_size().columns
		wait = int(argv[2])
		limit: int = 0 - abs(int(argv[1]))
		resp = requests.get(
			argv[3])
		jsdata: dict = resp.json()

		system('cls')
		ts = f">> {datetime.now().strftime(f'%X')} <<"
		# one timestamp at the top of the refresh

		print(border(ts))
		# -1 stop slice cuts the extra newline
		for i, m in enumerate(jsdata.values()):
			l = len(jsdata.values())
			# print only lines in the desired range
			if i > l + limit: print(f"{m[:-1]}")
			# countdown
		print(border('='))
		for j in tqdm(range(wait), bar_format=bar_format):
			sleep(1)

	except KeyboardInterrupt:
		logging.error("KeyboardInterrupt! Ok, byeeeee!")
		raise KeyboardInterrupt()