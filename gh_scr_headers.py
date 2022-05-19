from useful_func import jsonextr
"""
common variables for various scripts
"""

# load dict of config inputs
configs = jsonextr('gh_scr.json')

# output strings:
# ===============
paths = configs['output_filenames']

prv_store_list_repos = 'gh_scr/gh_rest_scr.01.csv'

logfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_LOG-{paths['scrape_itteration']}" +\
    f"{paths['log_ext']}"

debugfpath = \
    f"{paths['out_dir_main']}" +\
    f"gh_scr_DEBUG-{paths['scrape_itteration']}" +\
    f"{paths['log_ext']}"

# set up output file path string for scraped list to of stores to scrape
st_list_out_path: str = \
    paths['out_dir_main'] +\
    paths['store_scr'] +\
    paths['scrape_itteration'] +\
    paths['table_ext']

# set up output file path string for menu scrape
menu_out_path: str = \
    paths['out_dir_main'] +\
    paths['menu_scr'] +\
    paths['scrape_itteration'] +\
    paths['table_ext']

# set up output file path string for menu scrape
det_out_path: str = \
    paths['out_dir_main'] +\
    paths['det_scr'] +\
    paths['scrape_itteration'] +\
    paths['table_ext']

# set up output name string components to baqck up each scraped menu
# path for backup cacheection
cache_dir = \
    paths['out_dir_main']+\
    paths['scrape_itteration']+\
    paths['out_dir_collection_sub']
# ouptput filename string for backup csvs, a path, index and file ext will be added in func/loop
cache_fn = \
    paths['menu_scr'] +\
    paths['menu_scr_collection']
# extension
cache_ext = paths['table_ext']

if __name__ == '__main__':
    print(logfpath)
