from sys import argv
from gh_scr_headers import\
	debugfpath,\
	configs,\
	paths,\
	st_list_out_path,\
	logger_name_root,\
	scrape_iteration
from useful_fns.fns import input_y_no_loopother
import pandas as pd
from pandas import DataFrame as Df
import geopandas as gpd
from loggerhead import add_logger, add_handlers, wipe_files
from gh_scr import gh_store_scrape, wdriver_start, wdriver_quit
import traceback

# argv[1] should just be _, left same slices to match other scripts

re_file: int = None
if len(argv) >= 3:
	re_file = int(argv[2])
else:
	re_file = None

debugfpath = \
	f"{paths['out_dir_main']}" +\
	f"gh_scr_MENU-DEBUG-{scrape_iteration}" +\
	f"{paths['log_ext']}"

infofpath = \
	f"{paths['out_dir_main']}" +\
	f"gh_scr_MENU-CONSOLE-{scrape_iteration}" +\
	f"{paths['log_ext']}"

# get handlers for logging
handlers = add_handlers(debugfpath, infofpath)

# reset refile as proper bool
if re_file:
	refile: bool = True
else:
	refile: bool = False

if not refile:
	re_file = input_y_no_loopother(
		f"Restart Log Files?" +
		f"\t{debugfpath}, {infofpath}" +
		f"('Yes' will overwrite if these exist, else new log lines are appended) ")

if re_file:
	wipe_files(debugfpath, infofpath)

# configures main logging
# set up main logger
logger = add_logger(logger_name_root)
[logger.addHandler(h) for h in handlers]

# announce oneself
logger.info(__file__)


# # scrape of locations for further scrapes
# # =======================================
points_list_src = configs['pts_src_path']

def main():
	# prefix for output messages
	try:
		# gets series of points from calculated point grid
		coord_ser = gpd.read_file(points_list_src)['geometry'].apply(
			lambda x: tuple(
				str(x).replace('MULTIPOINT (', '').replace(')', '').split(' ')
			)
		)
		# 1,0 to switch lat, lng
		srch_coords = [(i[1], i[0]) for i in coord_ser]
		num_of_pts = len(srch_coords)
		logger.info(f"\tSearching {num_of_pts} points")

		# initialize chromedriver
		thisdriver = wdriver_start(True)

		st_res_df = Df()
		for for_idx, coords in enumerate(srch_coords):
			for_df = gh_store_scrape(loop_idx=for_idx,
				coords=coords, wdriver=thisdriver).drop_duplicates(subset='id')
			if len(for_df):
				st_res_df = pd.concat((st_res_df, for_df))

		wdriver_quit(thisdriver)

		# store list of restaurants locally


	except KeyboardInterrupt:
		logger.error(
			f"KeyboardInterrupt detected, bye-bye...")
		logger.debug(traceback.format_exc())
	except Exception:
		logger.error(f"An exceptionn occurred...")
		logger.debug(traceback.format_exc())
	finally:
		st_res_df.to_csv(st_list_out_path)
		logger.info(f"EXPORTED - {st_list_out_path}")

if __name__ == '__main__':
	main()