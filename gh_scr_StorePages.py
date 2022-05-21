import pandas as pd
from pandas import DataFrame as Df
from sys import argv
from gh_scr import\
    wdriver_start, wdriver_quit, rest_menu_scrape_n_scroll,\
    rest_details_scrape
from gh_scr_headers import\
    url_root, prv_store_list_repos, det_out_path, paths,\
    scrape_iteration, logger_name_root, cache_dir, cache_fn, cache_ext
from useful_func import input_y_no_loopother, Timekeeper
from loggerhead import add_logger, add_handlers, wipe_files, log_close
from logging import Logger
from datetime import datetime
now = datetime.now

# LOAD UP CMD LINE ARGS:
# ======================
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

bad_args_exception = Exception(f"Third arg must be 'menu' OR 'details'")
choice: str = None
if len(argv) >= 4:
    if (argv[3] in ['menu', 'details', 'both']):
        choice = str(argv[3])
    else: raise bad_args_exception
else: raise bad_args_exception
# ============================

# SET BOOLEANS FOR CASE (MENU OR DETAILS)
# =======================================
# bool tokens for case switches below
caser = { 'details': (False, True), 'menu': (True, False), 'both': (True, True) }
m, d =  caser[choice]
# ===================

# SET UP LOGGING:
# ===============
debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_{choice.upper()}-DEBUG-{scrape_iteration}" +\
    f"{paths['log_ext']}"

infofpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_{choice.upper()}-CONSOLE-{scrape_iteration}" +\
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
# ======================================

# announce oneself
logger.info(f"{__file__} ")


def main():
    list_len = len(st_res_df[pickup:])

    logger.info(f"SCRAPING {list_len} STORES")

    thisdriver = wdriver_start(True)

    # read in list of store
    st_res_df = pd.read_csv(prv_store_list_repos)

    # PRE-INITIALIZE OBJECTS FOR COUNTING/STORING:
    # ============================================
    # total results counter for menues
    if m: total_res: int = 0
    # initialize empty list to which series will be appended for details
    if d: rest_det_list = []

    # START TIMEKEEPING
    # =================
    tk = Timekeeper(len(st_res_df.index), now())

    # ANNOUNCE FUNCTION STARTUP:
    # ==========================
    logger.info(
        f"{choice.upper()} SCRAPING {len(st_res_df[pickup:])} STORES"
    )

    # THE LOOP
    # ========
    try:
        # SEPARATE NAMED LOGGER FOR THE FOR LOOP:
        for_logger: Logger = add_logger(f"{logger_name_root}.for-loop")

        for i, store in enumerate(st_res_df[pickup:].itertuples()):
            loop_id: str = f"{i}:{store.Index}|{store.name}|{store.id}"
            for_logger(f"\tStore list idx: {loop_id}")

            # initialize empty data frame for results of this loop iter
            if m: this_df = Df()        
            
            for_logger.info(f"\tStore list idx: {loop_id}")

            # start time loop time
            tk.step_clock_start(i, now())

            # SCRAPE PAGE RESULTS:
            # ====================
            try:
                url = f"{url_root}{store.url_path}"

                # use fn in core module to scrape details from store page on gh
                if d: this_ser = rest_details_scrape(url, store.id, store.name, thisdriver)
                if m: this_df = rest_menu_scrape_n_scroll(url, store.id, thisdriver)

            except Exception:
                for_logger.error(f"There was an exception while scraping")
                continue

            # RECORD STORE PAGE RESULTS:
            # ==========================
            # OUTPUT CSV FOR MENU SCRAPE, APPEND TO LIST OF SERIES FOR DETAILS SCRAPE
            if m:
                try:
                    if len(this_df.index):
                        # write to indiv csv
                        this_df.to_csv(f"{cache_dir}{cache_fn}{store.id}{cache_ext}")
                        total_res += len(this_df.index)
                        for_logger.info(f"\t\tTotal Results now: {total_res}")
                except Exception:
                    for_logger.error(f"There was an exception while writing to csv: {loop_id}")

            if d:
                try:
                    if this_ser.dtypes:
                        rest_det_list.append(this_ser)
                except Exception:
                    for_logger.error(f"\tNo results not stored for {loop_id}")
            # ================================================================

            # TIMEKEEPING WRAP-UP: (SAME FOR BOTH)
            # ====================================
            try:
                tk.step_clock_stop(now())
                est_t_remain = tk.remain_delta(2)
                est_t_elapsed = tk.total_elapse_delta(2)
                est_finish_at = tk.finish_time_strfmt(f"%m.%d %X")
                for_logger.info(
                    f"\tRetieved page details for {loop_id}, ~{tk.current_step_time:.2f} sec.")
                for_logger.info(
                    f"\t\tELAPS ~{est_t_elapsed}" +
                    f"\tETRmn ~{est_t_remain}" +
                    f"\tEst. finish: {est_finish_at}"
                )
            except Exception:
                for_logger.error(f"Timekeeping error: {loop_id}")
        # END LOOP
        # ========

        # OUTPUT DETAILS TO CSV: (DETAILS ONLY)
        if d:
            try:
                Df(rest_det_list).to_csv(det_out_path)
            except Exception:
                logger.error(f"There was an exception while writing full details results to {det_out_path}")
    
    # WRAP IT UP B! (same for both)
    # =============================
    finally:
        wdriver_quit(thisdriver)
        del thisdriver
        logger.info(f"***{len(rest_det_list)} PAGE DETAILS RETRIEVED***")
        return


if __name__ == '__main__':
    main()
    log_close(logger)
    
