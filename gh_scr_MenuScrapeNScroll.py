from sys import argv
from gh_scr import rest_menu_scrape_n_scroll, wdriver_start, wdriver_quit
from gh_scr_headers import\
    debugfpath,\
    prv_store_list_repos,\
    configs,\
    cache_dir,\
    cache_fn,\
    cache_ext,\
    paths
from useful_func import input_y_no_loopother, timedelta_float_2place, t_sec
import pandas as pd
from pandas import DataFrame as Df
import logging
from datetime import datetime
from loggerhead import std_hdlr, add_logger, log_config

# first cmd line arg, where to pick up in the list; defaults to 0
pickup: int
if len(argv) >= 2:
    pickup = int(argv[1])
else: pickup = 0

# whether to reset logs
re_file: int = None
if len(argv) >= 3:
    re_file = int(argv[2])
else: re_file = None

debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_MENU-DEBUG-{paths['scrape_itteration']}" +\
    f"{paths['log_ext']}"

# reset refile as proper bool
if re_file: refile: bool = True
else: refile: bool = False

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

st_res_df = pd.read_csv(prv_store_list_repos)

list_len = len(st_res_df[pickup:])

thisdriver = wdriver_start(True)

url_root = configs['store_scr_attrs']['url_root']

# initialize empty dataframe for full list of menu items
all_df = Df()

logger.info(f"SCRAPING {len(st_res_df)} MENUES FOR DETAILS")
start = t_sec()

# loop through all stores in list, starting at 'pickup' index
for_logger = add_logger('list_loop', __name__) # stream handler added in fn
for i, store in enumerate(st_res_df[pickup:].itertuples()):
    i_start = t_sec()
    this_df = Df()
    for_logger.info(f"\tStore list idx: {store.Index}\t{store.name}\t{store.id}")
    try:

        url = f"{url_root}{store.url_path}"

        this_df = rest_menu_scrape_n_scroll(url, store.id, thisdriver)

        for_logger.info(f"\t\tResults in this menu added to table: {len(this_df.index)}")

        if len(this_df.index):
            # add these results to total results
            all_df = pd.concat([all_df, this_df])

            # back up to indiv csv
            this_df.to_csv(f"{cache_dir}{cache_fn}{store.id}{cache_ext}")

    except Exception:
        for_logger.error(f"There was in issue menu scrapping {store.Index}: {store.name}, {store.id}")

    i_finish = t_sec()
    elapsed = float(i_finish - start)
    i_elapsed = float(i_finish - i_start)
    completed = i - pickup + 1
    remaining = list_len - completed
    avg_retrieve = float(elapsed / completed)
    t_remain = remaining * avg_retrieve
    est_t_remain = timedelta_float_2place(round(t_remain, 2))
    est_t_elapsed = timedelta_float_2place(round(elapsed, 2))
    finish_at = i_finish + t_remain
    est_finish_at = datetime.fromtimestamp(finish_at).strftime("%m.%d %X")

    logger.info(
        f"\t\tELAPS ~{est_t_elapsed}"+\
        f"\tETRmn ~{est_t_remain}" +
        f"\tEst. finish: {est_finish_at}"
    )

    logger.info(f"\t\tTotal Results now: {len(all_df)}\n")

wdriver_quit(thisdriver)
del thisdriver
        