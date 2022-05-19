import logging
from gh_scr_headers import debugfpath

fmt = '%(asctime)s:%(name)s:\n\t%(levelname)s: %(message)s'
datefmt = '%m.%d-%H:%M:%S'
formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

std_hdlr = logging.StreamHandler()
std_hdlr.setFormatter(formatter)
std_hdlr.setLevel(logging.INFO)

def add_logger(sffx: str, prefx: str = __name__):
    lggr = logging.getLogger(f"{prefx}.{sffx}")
    lggr.addHandler(std_hdlr)
    return lggr

# debug_hdlr = logging.FileHandler(debugfn)

def log_config(path: str=debugfpath, to_reset: bool=True):
    try:
        if to_reset:
            with open(debugfpath, 'w') as f:
                f.write('')

        logging.basicConfig(
            filename=path,
            filemode='a',
            format=fmt,
            datefmt=datefmt,
            level=logging.DEBUG,
            force=True
        )
    finally: return None
