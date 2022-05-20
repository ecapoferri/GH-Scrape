import json
from datetime import datetime, timedelta
from shapely.geometry import Point
from urllib.parse import urlencode

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


def query_url(api_url: str, args: dict, qmark: bool = True) -> str:
    """Assembles url with api parameters

    Args:
        api_url (str): api endpoint base url
            include reused parameters, set qmark to false to omit '?'
        args (dict): format pairs as <param>: <arg>
            use with your dynamic param/args
            use urllib.parse.quote to properly format strings as necessary
            before passing into this func
        qmark (bool, optional): Whether to include '?'. Defaults to True.

    Returns:
        str: full url encoded
    """
    q: str = '?' if qmark else ''
    f_args_str: str = urlencode(args)
    return f"{api_url}{q}{f_args_str}"


def ptstring_topoint(ptstr: str) -> Point:
    """
    Args:
        ptstr (str): string that has been converted from a shapely.geometry Point object

    Raises:
        Exception: general for any issues

    Returns:
        Point: shapely.geometry Point object
    """
    try:
        # 'POINT( ' 7 chars; ')' 1 char
        pS_list = ptstr[7:-1].split(" ")
        pF_list = [float(s) for s in pS_list]
        pt = Point(pF_list)
        return pt
    except ValueError:
        raise Exception(f"Something is wrong with the string passed to ptstring_topoint. " +
                        f"Maybe its not a shapely Point-like string.")
