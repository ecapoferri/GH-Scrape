import pandas as pd
from pandas import DataFrame as Df
from sys import argv
from gh_scr import\
    wdriver_start,\
    wdriver_quit,\
    rest_menu_scrape_n_scroll,\
    rest_details_scrape
from gh_scr_headers import\
    url_root,\
    prv_store_list_repos,\
    det_out_path,\
    paths, configs,\
    scrape_iteration,\
    logger_name_root,\
    cache_dir, cache_fn, cache_ext
from useful_func import input_y_no_loopother, Timekeeper
from loggerhead import add_logger, add_handlers, wipe_files
from datetime import datetime
now = datetime.now

# first cmd line arg, where to pick up in the list; defaults to 0
pickup: int
if len(argv) >= 2:
    pickup = int(argv[1])
else:
    pickup = 0

re_file: int = None
if len(argv) >= 3:
    re_file = int(argv[2])
else:
    re_file = None

script_choice: str = None
if len(argv) >= 4:
    script_choice = int(argv[3])
else:
    script_choice = 'details'

file_caser = {
    'details': 'DETAILS',
    'menu': 'MENU'
}

debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_{file_caser[script_choice]}-DEBUG-{scrape_iteration}" +\
    f"{paths['log_ext']}"

infofpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_{file_caser[script_choice]}-CONSOLE-{scrape_iteration}" +\
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


def details():
    list_len = len(st_res_df[pickup:])

    logger.info(f"SCRAPING {list_len} STORES FOR DETAILS")

    thisdriver = wdriver_start(True)

    # read in list of store
    st_res_df = pd.read_csv(prv_store_list_repos)

    # initialize empty dataframe for full list of menu items
    rest_det_list = []
    tk = Timekeeper(len(st_res_df.index), now())

    for_logger = add_logger(f"{logger_name_root}.for-loop")
    for i, store in enumerate(st_res_df[pickup:].itertuples()):
        loop_id: str = f"{i}:{store.Index}|{store.name}|{store.id}"
        for_logger(f"\tStore list idx: {loop_id}")

        # start time loop time
        tk.step_clock_start(i, now())

        try:
            # try:

            url = f"{url_root}{store.url_path}"

            # use fn in core module to scrape details from store page on gh
            this_ser = rest_details_scrape(
                url, store.id, store.name, thisdriver)
        except Exception:
            for_logger.error(f"There was an exception while scraping")
            continue

        try:
            if this_ser.dtypes:
                # add these results to total results
                rest_det_list.append(this_ser)
                # wasn't sure if i wanted to tie this to loop index or store
        except Exception:
            for_logger.error(f"\tReusults not stored for {loop_id}")

        try:
            tk.step_clock_stop(now())
            est_t_remain = tk.remain_delta(2)
            est_t_elapsed = tk.total_elapse_delta(2)
            est_finish_at = tk.finish_time_strfmt(f"%m.%d %X")
            for_logger.info(
                f"\tRetieved details for {loop_id}, ~{tk.current_step_time:.2f} sec.")
            for_logger.info(
                f"\t\tELAPS ~{est_t_elapsed}" +
                f"\tETRmn ~{est_t_remain}" +
                f"\tEst. finish: {est_finish_at}"
            )
        except Exception:
            for_logger.error(f"Timekeeping error: {loop_id}")

        # except Exception:
        #     logging.error(f"There was in issue menu scrapping {store.Index}: {store.name}, {store.id}")

    logger.info(f"***DETAILS FOR {len(rest_det_list)} RETRIEVED")

    Df(rest_det_list).to_csv(det_out_path)

    wdriver_quit(thisdriver)
    del thisdriver
    return


def menu():
    # total results counter
    total_res: int = 0
    
    st_res_df = pd.read_csv(prv_store_list_repos)

    list_len = len(st_res_df[pickup:])

    thisdriver = wdriver_start(True)

    url_root = configs['store_scr_attrs']['url_root']

    # initialize empty dataframe for full list of menu items

    logger.info(f"SCRAPING {len(st_res_df[pickup:])} MENUES FOR DETAILS")
    tk = Timekeeper(len(st_res_df.index), now())

    # loop through all stores in list, starting at 'pickup' index,
    # loop get's it's own logger to id problems there
    # for_logger = logging.getLogger(f"<root name>.list_loop") # stream handler added in fn
    # for_logger.addHandler(std_hdlr)
    for_logger = add_logger(f"{logger_name_root}.for-loop")
    try:
        for i, store in enumerate(st_res_df[pickup:].itertuples()):
            loop_id: str = f"{i}/{list_len}:idx-{store.Index}|{store.name}|{store.id}"

            # initialize empty data frame for results of this loop iter
            this_df = Df()
            
            for_logger.info(f"\tStore list idx: {loop_id}")
            # time keeping
            tk.step_clock_start(i, now())
            try:

                url = f"{url_root}{store.url_path}"

                this_df = rest_menu_scrape_n_scroll(url, store.id, thisdriver)

                for_logger.info(f"\t\tResults in this menu added to table: {len(this_df.index)}")
            except Exception:
                for_logger.error(f"There was an exceptionn while menu scrapping: {loop_id}")
                continue

            try:
                if len(this_df.index):
                    # write to indiv csv
                    this_df.to_csv(f"{cache_dir}{cache_fn}{store.id}{cache_ext}")
                    total_res += len(this_df.index)
                    for_logger.info(f"\t\tTotal Results now: {total_res}")
            except Exception:
                for_logger.error(f"There was an exception while writing to csv: {loop_id}")

            try:
                tk.step_clock_stop(now())
                est_t_remain = tk.remain_delta(2)
                est_t_elapsed = tk.total_elapse_delta(2)
                est_finish_at = tk.finish_time_strfmt(f"%m.%d %X")
                for_logger.info(
                    f"\tRetieved details for {loop_id}, ~{tk.current_step_time:.2f} sec.")
                for_logger.info(
                    f"\t\tELAPS ~{est_t_elapsed}" +
                    f"\tETRmn ~{est_t_remain}" +
                    f"\tEst. finish: {est_finish_at}"
                )
            except Exception:
                for_logger.error(f"Timekeeping error: {loop_id}")
    finally:
        if len(this_df.index) != 0:
            for_logger.info(f"\t\tRetrieved Menu Items: {len(this_df.index)}, ~{tk.current_step_time:.2f}, sec.")        
        wdriver_quit(thisdriver)
        del thisdriver
        return


fn_caser = {
    'details': details,
    'menu': menu
}

if __name__ == '__main__':
    fn_caser[script_choice]()
