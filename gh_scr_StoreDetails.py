from gh_scr import wdriver_start, wdriver_quit, rest_details_scrape
from gh_scr_headers import url_root, prv_store_list_repos, det_out_path, paths, scrape_iteration
from useful_func import timedelta_float_2place, input_y_no_loopother, t_sec
import logging
from loggerhead import add_logger, log_config
from datetime import datetime
import pandas as pd
from pandas import DataFrame as Df
from sys import argv

# first cmd line arg, where to pick up in the list; defaults to 0
pickup: int
if len(argv) >= 2:
    pickup = int(argv[1])
else:
    pickup = 0

# whether to reset logs, if true,
# files at the specified path will be overwritten with '' before logging here,
# else new log msgs will be appended
re_file: int = None
if len(argv) >= 3:
    re_file = int(argv[2])
else:
    re_file = None

debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_DETAILS-DEBUG-{scrape_iteration}" +\
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
logger = add_logger('')  # adds stream handler, info level
# announce oneself
logger.info(__file__)


def main():
    list_len = len(st_res_df[pickup:])

    logger.info(f"SCRAPING {list_len} STORES FOR DETAILS")
    start = datetime.now()

    thisdriver = wdriver_start(True)

    # read in list of store
    st_res_df = pd.read_csv(prv_store_list_repos)

    # initialize empty dataframe for full list of menu items
    rest_det_list = []

    for_logger = add_logger(f"{__name__}.for-loop")
    for i, store in enumerate(st_res_df[pickup:].itertuples()):
        loop_id: str = f"{i}:{store.Index}|{store.name}|{store.id}"
        logging.info(f"\tStore list idx: {loop_id}")

        # start time in sec, initialize finish time incase of error
        i_start = t_sec()
        i_finish = i_start
        try:
            # try:

            url = f"{url_root}{store.url_path}"

            # use fn in core module to scrape details from store page on gh
            this_ser = rest_details_scrape(url, store.id, store.name, thisdriver)

            # set finisht time in sec
            i_finish = t_sec()
        except Exception:
            logger.error(f"There was an exception while scraping")
            continue
        elapsed = float(i_finish - start)
        i_elapsed = float(i_finish - i_start)
        try:
            if this_ser.dtypes:
                # add these results to total results
                rest_det_list.append(this_ser)
                # wasn't sure if i wanted to tie this to loop index or store
                logger.info(
                    f"\tRetieved details for {loop_id}, ~{i_elapsed:.2f} sec.")
        except Exception:
            logger.error(f"\tReusults not stored for {loop_id}")

        try:
            completed = store.Index - pickup + 1
            remaining = list_len - completed
            avg_retrieve = float(elapsed / completed)
            t_remain = remaining * avg_retrieve
            est_t_remain = timedelta_float_2place(round(t_remain, 2))
            est_t_elapsed = timedelta_float_2place(round(elapsed, 2))
            finish_at = i_finish + t_remain
            est_finish_at = datetime.fromtimestamp(finish_at).strftime("%m.%d %X")
            logger.info(
                f"\t\tELAPS ~{est_t_elapsed}" +
                f"\tETRmn ~{est_t_remain}" +
                f"\tEst. finish: {est_finish_at}"
            )
        except Exception:
            logger.error(f"Timekeeping error: {loop_id}")        

        # except Exception:
        #     logging.error(f"There was in issue menu scrapping {store.Index}: {store.name}, {store.id}")

    logger.info(f"***DETAILS FOR {len(rest_det_list)} RETRIEVED")

    Df(rest_det_list).to_csv(det_out_path)

    wdriver_quit(thisdriver)
    del thisdriver
    return


if __name__ == '__main__':
    main()
