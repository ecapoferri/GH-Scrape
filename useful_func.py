import json
from datetime import datetime, timedelta
from shapely.geometry import Point
from urllib.parse import urlencode

# TODO fix except clauses

def td_string(seconds: float, places: int) -> str:
    tdstr = str(timedelta(seconds=seconds))
    parts = tdstr.split('.')
    print(seconds)
    if len(parts) > 1:
        if len(parts[1]) < places: places = len(parts[1])
    else: parts.append(str(0).zfill(places))
    return f"{parts[0]}.{parts[1][:places]}"

class Timekeeper:
    tot_steps: int = None
    clock_start: float = None
    step_start: float = None
    current_step_index: int = None
    step_finish: float = None
    step_avg_time: float = None
    total_elapsed: float = None
    steps_completed: int = None
    step_avg_time: float = None
    est_time_remain: float = None
    est_finish: datetime = None

    def __init__(self, tot_steps: int, run_start: datetime):
        self.tot_steps = tot_steps
        self.clock_start = run_start.timestamp()
        self.step_start = self.clock_start

    def step_clock_start(self, step_index: int, timenow: datetime):
        self.step_start = timenow.timestamp()
        self.step_finish = self.step_start
        self.current_step_index = step_index
        return

    def step_clock_stop(self, timenow: datetime):
        self.step_finish = timenow.timestamp()
        if self.step_start <= self.clock_start:
            raise Exception(
                f"Timekeeper: step_clock_start has not been called. step_clock_start must be called or step_start attribute must be changed.")
        self.total_elapsed = self.step_finish - self.clock_start
        self.steps_completed = self.current_step_index + 1
        self.steps_remaining = self.tot_steps - self.steps_completed
        self.current_step_time = self.step_finish - self.step_start
        self.step_avg_time = self.total_elapsed / self.steps_completed
        self.est_time_remain = self.steps_remaining * self.step_avg_time
        self.est_finish = datetime.fromtimestamp(self.step_finish + self.est_time_remain)
        return

    def step_update(self, **new_step_info):
        """to get different time estimate values if you need a different type of step estimate"""

        if self.step_finish <= self.step_start:
            raise Exception(
                f"Timekeeper: step_clock_stop has not been called. step_clock_stop must be called or step_finish attribute must be changed.")
        if ('new_steps_remaining' in new_step_info) &\
            ('new_total_steps' in new_step_info) &\
                ('new_steps_completed' in new_step_info):
            self.steps_remaining = new_step_info['new_steps_remaining']
            self.tot_steps = new_step_info['new_total_steps']
            self.steps_completed = new_step_info['new_steps_completed']

        self.steps_remaining = self.tot_steps - self.steps_completed
        self.step_avg_time = self.total_elapsed / self.steps_completed
        self.est_time_remain = self.steps_remaining * self.step_avg_time
        self.est_finish = datetime.fromtimestamp(self.step_finish + self.est_time_remain)
    
    def remain_delta(self, roundto: int) -> str:
        return td_string(self.est_time_remain, roundto)

    def total_elapse_delta(self, roundto: int) -> str:
        return td_string(self.total_elapsed, roundto)

    def avg_delta(self, roundto: int) -> str:
        return td_string(self.step_avg_time, roundto)

    def avg_sec(self, roundto: int) -> float:
        return round(self.est_time_remain, roundto)

    def finish_time(self) -> datetime:
        return self.est_finish

    def finish_time_strfmt(self, strftime: str) -> str:
        return self.est_finish.strftime(strftime)

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
