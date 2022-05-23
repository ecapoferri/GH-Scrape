import logging
from sys import stderr

"""
used to set up common logging for scripts and modules in this proect
"""
debug_fmt = f"%(asctime)s >> %(name)s [%(module)s.%(funcName)s] >>\n\t%(levelname)s: %(message)s"
debug_datefmt = f'%m.%d-%H:%M:%S'
info_fmt = f"%(asctime)s >> %(message)s"
strm_fmt = f"%(name)s\t%(levelname)s:\t%(message)s"
strm_datefmt = f"%H:%M:%S"

debug_fmtter = logging.Formatter(fmt=debug_fmt, datefmt=debug_datefmt)
info_fmtter = logging.Formatter(fmt=info_fmt, datefmt=strm_datefmt)
strm_fmtter = logging.Formatter(fmt=strm_fmt)


def wipe_files(*args):
    for file in args:
        with open(file, 'w') as f:
            f.write('')
    return


def add_handlers(debug_f_path, info_f_path):
    debug_hdlr = logging.FileHandler(debug_f_path, 'a')
    debug_hdlr.setFormatter(debug_fmtter)
    debug_hdlr.setLevel(logging.DEBUG)

    info_hdlr = logging.FileHandler(info_f_path, 'a')
    info_hdlr.setFormatter(info_fmtter)
    info_hdlr.setLevel(logging.INFO)

    std_hdlr = logging.StreamHandler(stderr)
    std_hdlr.setFormatter(strm_fmtter)
    std_hdlr.setLevel(logging.ERROR)
    return debug_hdlr, info_hdlr, std_hdlr

def add_logger(lggr_name: str, *hdlrs) -> logging.Logger:
    """
    Returns a logging.Logger with an ERROR level streamhandler,
    an INFO level filehandler, and a DEBUG level filehandler
    """
    lggr = logging.getLogger(lggr_name)
    lggr.setLevel(logging.DEBUG)
    return lggr


def log_close(lggr: logging.Logger) -> None:
    [logging.info(f"Logger: {lggr.name}'s handlers will be closed.")]
    [h.close for h in lggr.handlers]
    return