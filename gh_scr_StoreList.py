from sys import argv
from gh_scr_headers import\
    debugfpath,\
    configs,\
    paths,\
    st_list_out_path
from useful_func import input_y_no_loopother
import pandas as pd
from pandas import DataFrame as Df
import geopandas as gpd
import logging
from loggerhead import std_hdlr, add_logger, log_config
from gh_scr import gh_store_scrape, wdriver_start, wdriver_quit

# first cmd line arg, where to pick up in the list; defaults to 0
pickup: int
if len(argv) >= 2:
    pickup = int(argv[1])
else:
    pickup = 0

# whether to reset logs
re_file: int = None
if len(argv) >= 3:
    re_file = int(argv[2])
else:
    re_file = None

debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_STORE-DEBUG-{paths['scrape_itteration']}" +\
    f"{paths['log_ext']}"

# reset refile as proper bool
if re_file:
    refile: bool = True
else:
    refile: bool = False

if not refile:
    re_file = input_y_no_loopother(
        f"Restart Log Files?" +
        f"\t{debugfpath}" +
        f"('Yes' will overwrite if these exist, else new log lines are appended) "
    )
# configures main logging
log_config(path=debugfpath, to_reset=re_file)
# set up main logger
logger = logging.getLogger()
# adds stream handler, info level
logger.addHandler(std_hdlr)
logger.info(__file__)


# # scrape of locations for further scrapes
# # =======================================
points_list_src = configs['pts_src_path']

def main():
    # prefix for output messages
    fn_logger = add_logger(main.__name__, __name__)
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
        fn_logger.info(f"\tSearching {num_of_pts} points")

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
        fn_logger.error(
            f"KeyboardInterrupt detected, bye-bye...")
    except Exception:
        fn_logger.error(f"An exceptionn occurred...")
    finally:
        st_res_df.to_csv(st_list_out_path)
        fn_logger.info(f"EXPORTED - {st_list_out_path}")