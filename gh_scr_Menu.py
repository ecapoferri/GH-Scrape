from sys import argv
from gh_scr import rest_menu_scrape_n_scroll, wdriver_start, wdriver_quit
from gh_scr_headers import\
    prv_store_list_repos,\
    configs,\
    cache_dir,\
    cache_fn,\
    cache_ext,\
    paths,\
    scrape_iteration,\
    logger_name_root
from useful_func import input_y_no_loopother, timedelta_float_2place, t_sec
import pandas as pd
from pandas import DataFrame as Df
from datetime import datetime
from loggerhead import add_logger, wipe_files, add_handlers

# first cmd line arg, where to pick up in the list; defaults to 0
pickup: int
if len(argv) >= 2:
    pickup = int(argv[1])
else: pickup = 0

re_file: int = None
if len(argv) >= 3:
    re_file = int(argv[2])
else: re_file = None

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
if re_file: refile: bool = True
else: refile: bool = False

if not refile:
    re_file = input_y_no_loopother(
        f"Restart Log Files?" +
        f"\t{debugfpath}, {infofpath}" +
        f"('Yes' will overwrite if these exist, else new log lines are appended) ")

if re_file: wipe_files(debugfpath, infofpath)

# configures main logging
# set up main logger
logger = add_logger(logger_name_root)
[logger.addHandler(h) for h in handlers]

# announce oneself
logger.info(__file__)


def main():
    # total results counter
    total_res: int = 0
    
    st_res_df = pd.read_csv(prv_store_list_repos)

    list_len = len(st_res_df[pickup:])

    thisdriver = wdriver_start(True)

    url_root = configs['store_scr_attrs']['url_root']

    # initialize empty dataframe for full list of menu items

    logger.info(f"SCRAPING {len(st_res_df[pickup:])} MENUES FOR DETAILS")
    start = t_sec()

    # loop through all stores in list, starting at 'pickup' index,
    # loop get's it's own logger to id problems there
    # for_logger = logging.getLogger(f"{__name__}.list_loop") # stream handler added in fn
    # for_logger.addHandler(std_hdlr)
    for_logger = add_logger(f"{__name__}.for-loop")
    try:
        for i, store in enumerate(st_res_df[pickup:].itertuples()):
            loop_id: str = f"{i}/{list_len}:idx-{store.Index}|{store.name}|{store.id}"
            # time keeping
            i_start = t_sec()
            i_finish = i_start
            # initialize empty data frame for results of this loop iter
            this_df = Df()
            
            for_logger.info(f"\tStore list idx: {loop_id}")
            try:

                url = f"{url_root}{store.url_path}"

                this_df = rest_menu_scrape_n_scroll(url, store.id, thisdriver)

                for_logger.info(f"\t\tResults in this menu added to table: {len(this_df.index)}")
            except Exception:
                for_logger.error(f"There was an exceptionn while menu scrapping: {loop_id}")
                continue
            i_finish = t_sec()
            elapsed = float(i_finish - start)
            i_elapsed = float(i_finish - i_start)
            if len(this_df.index) != 0:
                for_logger.info(f"\t\tRetrieved Menu Items: {len(this_df.index)}, ~{i_elapsed:.2f}, sec.")        
            try:
                if len(this_df.index):
                    # write to indiv csv
                    this_df.to_csv(f"{cache_dir}{cache_fn}{store.id}{cache_ext}")
                    total_res += len(this_df.index)
                    for_logger.info(f"\t\tTotal Results now: {total_res}")
                    i_finish = t_sec()
            except Exception:
                for_logger.error(f"There was an exception while writing to csv: {loop_id}")

            try:

                completed = store.Index - pickup + 1
                remaining = list_len - completed
                avg_retrieve = float(elapsed / completed)
                t_remain = remaining * avg_retrieve
                est_t_remain = timedelta_float_2place(round(t_remain, 2))
                est_t_elapsed = timedelta_float_2place(round(elapsed, 2))
                finish_at = i_finish + t_remain
                est_finish_at = datetime.fromtimestamp(finish_at).strftime("%m.%d %X")

                for_logger.info(
                    f"\t\tELAPS ~{est_t_elapsed}"+\
                    f"\tETRmn ~{est_t_remain}" +
                    f"\tEst. finish: {est_finish_at}"
                )

            except Exception:
                for_logger.error(f"Timekeeping error: {loop_id}")
    finally:
        wdriver_quit(thisdriver)
        del thisdriver
        return

if __name__ == '__main__':
    main()
        