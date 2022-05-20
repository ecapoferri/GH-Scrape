import logging

"""
used to set up common logging for scripts and modules in this proect
"""

debugfpath = 'testlogout.log'

fmt = "%(asctime)s >> %(name)s [%(module)s.%(funcName)s] >>\n\t%(levelname)s: %(message)s"
datefmt = '%m.%d-%H:%M:%S'
formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

std_hdlr = logging.StreamHandler()
std_hdlr.setFormatter(formatter)
std_hdlr.setLevel(logging.INFO)

def add_logger(lggr_name: str) -> logging.Logger:
    """
    Returns a logging.Logger with an INFO level StreamHandler
    """
    lggr = logging.getLogger(f"{lggr_name}")
    lggr.addHandler(std_hdlr)
    lggr.info(f"Starting logger: {lggr_name}")
    return lggr

# debug_hdlr = logging.FileHandler(debugfn)

def log_config(path: str=debugfpath, to_reset: bool=True):
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
    logging.info(f"Starting this log: {path}")
    return
