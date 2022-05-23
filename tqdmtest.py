from ast import expr
from tqdm import tqdm
from time import sleep
from datetime import datetime
from os import system, get_terminal_size


w = get_terminal_size().columns
ts = f">> {datetime.now().strftime(f'%X')} <<"
print(str(ts).center(w, '-'))
print("\n\n\n")
for i in tqdm(range(10),
              bar_format='REFRESH IN: {remaining_s:.0f} s |{bar}| (** ^C to EXIT **)'
):
	sleep(0.4)
