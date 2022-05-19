import json
from datetime import datetime, timedelta
import logging

# TODO fix except clauses

def timedelta_float_2place(secs: float) -> str:
    return str(timedelta(seconds=secs)).split('.')[0]


def ts() -> str:
    """Quick Timestamp: mm.dd-hh.mm.ss"""
    return datetime.now().strftime('%m.%d-%H.%M.%S')


def t_sec() -> float:
    return float(datetime.now().timestamp())


def jsonextr(filename: str) -> dict:
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    return data


def input_y_otherfalse(qu: str) -> bool:
    to_cont = False
    try:
        while True:
            yn = input(f"{qu}")
            if str(yn).lower() in ['y', 'yes']:
                to_cont = True
                break
            else:
                to_cont = False
                break
    except ValueError:
        to_cont = False
        raise Warning(
            "Had a problem with input question. Set to False by default."
        )
    except KeyboardInterrupt:
        to_cont = False
        raise KeyboardInterrupt(
            "Input question got a keyboard interrupt during input. Set to False by default."
        )
    finally:
        return to_cont

# def input_y_n_cancel(qu) -> None:
#     print("still need to write this function...")
#     pass


def input_y_no_loopother(qu: str) -> bool:
    to_cont = None
    yn = None
    try:
        while not yn:
            yn = input(f"{qu} Y/N:")
            if str(yn).lower() in ['y', 'yes']:
                to_cont = True
                break
            else:
                if str(yn).lower() in ['n', 'no']:
                    to_cont = False
                    break
                else:
                    yn = None
                    to_cont = False
                    print(f"\nTry again, won't you?\t")
                    continue

    except ValueError:
        to_cont = False
        raise Warning(
            "Had a problem with 'Y/N' input. Set to False by default."
        )
    except KeyboardInterrupt:
        to_cont = False
        raise KeyboardInterrupt(
            "'Y/N' got keyboard interrupt during input. Set to False by default."
        )
    finally:
        return to_cont


def input_y_otherfalse(qu: str) -> bool:
    to_cont = False
    try:
        yn = input(f"{qu}")
        if str(yn).lower() in ['y', 'yes']:
            to_cont = True
        else:
            to_cont = False
    except ValueError:
        to_cont = False
        raise Warning(
            "Had a problem with input question. Set to False by default."
        )
    except KeyboardInterrupt:
        to_cont = False
        raise KeyboardInterrupt(
            "Input question got a keyboard interrupt during input. Set to False by default."
        )
    finally:
        return to_cont

# def input_y_n_cancel(qu) -> None:
#     print("still need to write this function...")
#     pass


def input_y_default(qu: str) -> bool:
    to_cont = False
    try:
        yn = input(f"{qu} [Y]/n:")
        if str(yn).lower() in ['n', 'no']:
            to_cont = False
        else:
            to_cont = True

    except ValueError:
        to_cont = False
        raise Warning(
            "Had a problem with 'Y/N' input. Set to False."
        )
    except KeyboardInterrupt:
        to_cont = False
        raise KeyboardInterrupt(
            "'Y/N' got keyboard interrupt during input. Set to False."
        )
    finally:
        return to_cont


def str_to_list(the_string: str):
    the_list = str(the_string).replace('[', '').replace(
        ']', '').replace("'", '').split(', ')
    return the_list



