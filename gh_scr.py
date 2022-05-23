from typing import Type
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as Bs
from bs4.element import Tag
from time import sleep
import pandas as pd
from pandas import DataFrame as Df, Series as Ser
import logging
from useful_func import ts, jsonextr, query_url
from loggerhead import add_logger


# TODO change json to .env and use dotenv
config_args = jsonextr('gh_scr.json')
logger_name_root = config_args['logger_name_root']

# start logger as defined in loggerhead, debug to file,
# adds a common streamhandler, info level to console
logger = add_logger(f"{logger_name_root}.{__name__}")

# read in default values for scrapes:
# ===================================
wd_path = config_args['wd_path']
url_verbose = config_args['url_verbose']

# VARIABLE shorthands
# *_avd: <attribute>: <value> Dictionary,
#   as in <tag attribute=value ></tag>;
#   for 'bs.find(attrs=var_avd)'
# *_a: <attribute> str only
# *_v: attribute Value str only
# *_xp: xpath str
# *_cs: class selector str


# store default values:
# =====================
# root of store scrape url
st_url: dict = config_args['store_scr_url']
st_url_root: str = st_url['root']
st_url_params: dict = st_url['params']
# dict keys for url args
lat_k = st_url_params['lat']
lng_k = st_url_params['lng']
pg_k = st_url_params['page_num']
# wait times for store scrape
st_wait_time_A = config_args['store_scr_wait_time_1stpg']
st_wait_time = config_args['store_scr_wait_time']
st_col_hds = config_args['store_scr_col_hds']
st_attrs = config_args['store_scr_attrs']
# bs.find() values
# xpath to popup botton, need to 'click' to advance wdriver
st_button_xp = st_attrs['button_xp']
# class selector for each search result
st_srch_res_cs = st_attrs['srch_res_cs']
# store id attribute of parent element
store_id_a = st_attrs['store_id_a']
# xpath to footer on results page
st_res_footer_xp = st_attrs['res_footer_xp']
# names of series/df columns for store list
st_idcol = st_col_hds['store_id']
st_nmcol = st_col_hds['store_name']
st_urcol = st_col_hds['store_url_path']
# ordered to apply to series for store list
st_cols = (st_idcol, st_nmcol, st_urcol)


def gh_srch_url(
    root: str,
    *args,
    keys: tuple=(lat_k, lng_k, pg_k)
) -> str:
    """used to construct urls during loop over for the search

        Args:
            root (str): url root
            optional args, ordered:
                latitutde (float), longitude(float), page number (int)
            keys (tuple): keys to be assigned as parameter names
                Default assigned in module through input config

        Returns:
            str: final url
        """
    
    url_args = dict()
    if args:
        for i, v in enumerate(args):
            url_args[keys[i]] = v

    return query_url(root, url_args)


def default_wait_for(wd: webdriver.Chrome) -> WebElement:
    return wd.find_element_by_tag_name('html').get_attribute('innerHTML')


def load_html(url: str, wdriver: webdriver.Chrome,
    wait_for_fn: Type['function']=default_wait_for,
    wait_time: float = 1, load_anew: bool = True
):

    """_summary_

    Args:
        url (str): url for webdriver to get
        wdriver (webdriver.Chrome): instance of webdriver.Chrome
        wait_for_fn (function): function to execute.
            Default is lambda wd: wd.find_element_by_tag_name('html').get_attribute('innerHTML')
        wait_time (float, optional): time to wait for results. Defaults to 1.
            ***this is doubled in the fn!***
        load_anew (bool): whether to get html or just return new html_str. Default to True

    Raises:
        KeyboardInterrupt
    """

    try:
        # get html from page
        if load_anew:
            wdriver.get(url)
            sleep(wait_time)

        wdriver.execute_script("document.body.style.zoom='25%'")
        logger.debug(f"{url}")

        return WebDriverWait(
            wdriver, timeout=wait_time, poll_frequency=1
        ).until(lambda d: wait_for_fn(d))

    except KeyboardInterrupt:
        raise KeyboardInterrupt(" gh_scr.load_html: KeyboardInterrupt detected...")
    except Exception:
        logger.error(f"Problem with webdriver wait on {url}")



def gh_store_scrape(
    coords: tuple,
    wdriver: webdriver.Chrome,
    url_root: str=st_url_root,
    res_footer_xp: str=st_res_footer_xp,
    wait_time: float=st_wait_time,
    srch_res_cs: str=st_srch_res_cs,
    wait_time_pg1: float=st_wait_time_A,
    loop_idx: int=None
) -> Df:
    """scrape store results from 

    Args:
        coords (tuple): _description_
        wdriver (webdriver.Chrome): _description_
        url_root (str, optional): _description_. Defaults to st_url_root.
        res_footer_xp (str, optional): _description_. Defaults to st_res_footer_xp.
        wait_time (float, optional): _description_. Defaults to st_wait_time.
        srch_res_cs (str, optional): _description_. Defaults to st_srch_res_cs.

    Returns:
        Df: _description_
    """

    # initialize list of html strings
    page_htmls = []

    # list of series to dataframe to append all results
    st_sers = []
    
    try:
        try:
            if not loop_idx:
                loop_idx: str = f"NoIdx"

            # for idx, coords in enumerate(coords_list):
            log_str = \
                f"Store Search Loop:\n" +\
                f"  Search:{str(loop_idx).zfill(4)},"+\
                f"\tSearch Point:{coords[0]},{coords[1]}"

            # construct initial url
            url = gh_srch_url(url_root, coords[0], coords[1])
            logger.debug(f"\turl: {url}")

            html_str = load_html(url=url, wdriver=wdriver, wait_time=wait_time_pg1)

            page_htmls.append(html_str)

            # find number of results pages, in page text 1 of XX in the footer
            res_footer = wdriver.find_element_by_xpath(res_footer_xp)

            pg_text: str = res_footer.text
            pgs = int(pg_text.split('of ')[-1])
            pg_status = ''
            # add reults info to logging output
            if pgs:
                log_str += f"\tPgs of Results: {str(pgs)}"
                logger.info(log_str)
                pg_status += f"\t{ts()}: Pg 1..OK; "
                del log_str
            else:
                logger.info(log_str)
                del log_str
                logger.error(f"Did not get total results for {coords}")

            # loop through remaining pages and add strings of html to the list, start with second page
            for pg in range(2, pgs+1, 1):
                try:
                    # retrieve html from subsequent pages
                    url = gh_srch_url(url_root, coords[0], coords[1], pg)

                    next_html_str = load_html(url=url, wdriver=wdriver, wait_time=wait_time)
                    page_htmls.append(next_html_str)
                    pg_status +=  f"{ts()}: Pg {pg}..OK; "
                    
                except Exception:
                    logger.error(f"\tThere was an issue with page {pg} for {coords}")

            logger.info(pg_status)

        except Exception:
            logger.error(f"There was a problem getting search results for {coords}, see above?")

        try:
            # bs list of all search result store parent elements by class selector
            res_pgs = [
                Bs(h, 'html.parser').find_all(class_=srch_res_cs) for h in page_htmls
            ]
            # loop through list of lists of found elements
            for srch_els in res_pgs:
                # loop through found elements in each list
                for el in srch_els:
                    try:
                        # store id
                        id = int(el.attrs[store_id_a])
                        # store info element, contains name in text and url in link attribute
                        name_url = el.find('a', class_="restaurant-name")
                        name = name_url.string
                        url = name_url.attrs['href']

                        res_ser = Ser((id, name, url,), st_cols)

                        # append results data to indiv. row each time
                        st_sers.append(res_ser)
                    except Exception:
                        logger.error(f"gh_scr.gh_store_scrape, search results element loop: Store info not found in an element from {coords}")
        except Exception:
            logger.error(f"gh_scr.gh_store_scrape: Exception in list of results elements or extraction of data from {coords}\n{url}.")

    except KeyboardInterrupt:
        raise KeyboardInterrupt(
            "gh_scr.gh_store_scrape: KeyboardInterrupt detected...")
    finally:
        # finally, put all series of search reults into a df
        if len(st_sers) !=0 :
            pass
        else:
            logger.error(f"gh_scr.gh_store_scrape: No Results returnedfor {coords}")
            logger.debug(f"\tBad search results scrape for {coords}\n\turl: {url}")
        
        # dataframes list of series of store results to return
        return Df(st_sers)


def wdriver_start(headless: bool, ex_path: str = wd_path) -> webdriver.Chrome:
    """create an intance of webdriver.Chrome for use in scraping;
        useful for keeping wdriver open to save time while iterating through
        multiple search loops; easy to kill with gh_scr.driver_quit

    Args:
        headless (bool): headless option to instantiate object with
            if headless=True, window size cmd arg will be passed as "--window-size=1920,1200"
        wd_path (str, optional): path to webdriver executable. Defaults to wd_path in gh_scr.json

    Returns:
        webdriver.Chrome object to pass into scrape fns
    """
    # initialize webdriver
    # try:
    options = Options()
    options.headless = headless
    if headless:
        for o in "--window-size=1920,1200", "--disable-gpu", "--no-sandbox":
            options.add_argument(o)
    else: options.add_argument("--window-size=800,1200")
    return webdriver.Chrome(executable_path=ex_path, options=options)
    # except Exception:
    #     err_msg = f"Was not able to init webdriver in gh_scr.wdriver. See debug for arg dump."
    #     logger.error(err_msg)
    #     for var in ("headless", headless), ("ex_path", ex_path):
    #         logger.debug(f"arg: {var[0]} = {var[1]}")
    #     raise Exception(err_msg)

def scroll_home(wdr: webdriver.Chrome):
    sh: ActionChains = ActionChains(wdr).send_keys(Keys.HOME)
    sh.perform()


def scroll_end(wdr: webdriver.Chrome):
    sh: ActionChains = ActionChains(wdr).send_keys(Keys.END)
    sh.perform()


def wdriver_quit(wdrv: webdriver.Chrome) -> None:
    """Citizen, give me a selenium.webdriver object. I will quit it for you."""
    wdrv.quit()
    logger.info(f"webdriver, session id: {wdrv.session_id} has quit! Have a nice day!")


# menu default values:
# ====================
# bs.find() keys
m_attrs = config_args['menu_scr_attrs']
# column head names for results
m_col_hds = config_args['menu_scr_col_hds']

# menu item attribute and value
m_itm_main_avd = m_attrs['parent_avd']
m_itm_price_avd = m_attrs['price_avd']
m_itm_id_a = m_attrs['id_a']
m_itm_nm_avd = m_attrs['name_avd']
m_itm_de_avd = m_attrs['descr_avd']
# xpath to popup botton
m_button_txt = m_attrs['button_txt']

# names of series/df columns
m_idcol = m_col_hds['item_id']
m_nmcol = m_col_hds['item_name']
m_prcol = m_col_hds['item_price']
m_dscol = m_col_hds['item_descr']

menu_wait_time = float(config_args['menu_scr_wait_time'])

# ordered to apply to series
m_cols = (m_idcol, m_nmcol, m_prcol, m_dscol)

def ser_item_details(
    i_el: Bs,
    itm_id_a: str,
    itm_price_avd: dict,
    itm_nm_avd: dict,
    itm_de_avd: dict,
    cols: tuple,
) -> Ser:
    """"get item details from a menu parent page element"""

    debug_str = ''
    # menu item id
    i_id = i_el.attrs[itm_id_a]
    i_id = int(i_id)
    debug_str += f"item info: {i_id}; "

    # menu item price / remove $ sign, make float
    i_pr = i_el.find(attrs=itm_price_avd).string
    i_pr = float(i_pr[1:])
    debug_str += f"item info: {i_pr}; "

    # menu item name
    i_nm: str = i_el.find(attrs=itm_nm_avd).string
    debug_str += f"item info: {i_nm}; "

    # item description if it exists, it's a little weird, seems to be second to last of 5 span elements if there, before the last two are the price twice
    i_de = i_el.find(attrs=itm_de_avd).string
    debug_str += f"item info: {i_de}; "

    logger.debug(f"\t{debug_str}")
    del debug_str

    # id, name, price, description
    return Ser((i_id, i_nm, i_pr, i_de), index=cols) 


def rest_menu_scrape(
    url: str,
    store_id: int,
    wdriver: webdriver.Chrome,
    wait_time: float = menu_wait_time,
    itm_avd: str = m_itm_main_avd,
    itm_price_avd: str = m_itm_price_avd,
    itm_id_a: str = m_itm_id_a,
    itm_nm_avd: str = m_itm_nm_avd,
    itm_de_avd: str = m_itm_de_avd,
    cols: tuple = m_cols,
    idcol: str = m_idcol
) -> Df:
    """grubhub menu page

    Args:
        url (str): _description_
        store_id (int): store id to be added to df
        wdriver (Chromedriver object)
            create a webdriver with gh_scr.wdriver and pass it to this fn
            this is to keep the wdriver open during looping iterations to save on time
            kill the wdriver session with gh_scr.driver_quit(your_wdriver)
    (Following set by json config but can be)
        wd_path (str, optional): _description_. Defaults to wd_path.
        menu_wait_time (float, optional): _description_. Defaults to menu_wait_time.
        button_xp (str, optional): _description_. Defaults to button_xp.
        m_itm_main_avd (str, optional): _description_. Defaults to m_itm_main_avd.
        itm_id_a (str, optional): _description_. Defaults to itm_id_a.
        cols (tuple, optional): _description_. Defaults to cols.

    Raises:
        Warning:
        Warning:
        Exception:

    Returns:
        pd.DataFrame: contains all menu items plus store id
            can be concatenated to make one large master
            
    """

    try:
        html_str = load_html(url=url, wdriver=wdriver, wait_time=wait_time)

        # bs list of all menu item parent elements
        menu_els = Bs(html_str, 'html.parser').find_all(attrs=itm_avd)
        del html_str
        logger.debug(f"Menu elements: {len(menu_els)}")

        # loop through each element in menu_els
        ser_list = []
        for idx, i in enumerate(menu_els):
            try:
                i_ser = ser_item_details(
                    i_el=i,
                    itm_id_a=itm_id_a,
                    itm_price_avd=itm_price_avd,
                    itm_nm_avd=itm_nm_avd,
                    itm_de_avd=itm_de_avd,
                    cols=cols
                )

                # add series to list of series for dataframe from this url
                ser_list.append(i_ser)

            except Exception:
                logger.error(
                    f"Somethind went wrong on menu element {idx} from {url}")

        # results to dataframe
        df = Df(ser_list).drop_duplicates(subset=idcol).reset_index(drop=True)
        # set a column store_id will be foreign key for each store
        df['store_id'] = store_id

        return df
    except Exception:
        logger.error(
            f"There was an an exception in rest_menu_scrape with {url}")


def rest_menu_scrape_n_scroll(
    url: str,
    store_id: int,
    wdriver: webdriver.Chrome,
    wait_time: float=menu_wait_time,
    itm_avd: str=m_itm_main_avd,
    itm_price_avd: str=m_itm_price_avd,
    itm_id_a: str=m_itm_id_a,
    itm_nm_avd: str=m_itm_nm_avd,
    itm_de_avd: str=m_itm_de_avd,
    cols: tuple=m_cols,
    idcol: str=m_idcol
) -> Df:

    """grubhub menu page

    Args:
        url (str): _description_
        store_id (int): store id to be added to df
        wdriver (Chromedriver object)
            create a webdriver with gh_scr.wdriver and pass it to this fn
            this is to keep the wdriver open during looping iterations to save on time
            kill the wdriver session with gh_scr.driver_quit(your_wdriver)
    (Following set by json config but can be)
        wd_path (str, optional): _description_. Defaults to wd_path.
        menu_wait_time (float, optional): _description_. Defaults to menu_wait_time.
        button_xp (str, optional): _description_. Defaults to button_xp.
        m_itm_main_avd (str, optional): _description_. Defaults to m_itm_main_avd.
        itm_id_a (str, optional): _description_. Defaults to itm_id_a.
        cols (tuple, optional): _description_. Defaults to cols.

    Returns:
        pd.DataFrame: contains all menu items plus store id
            can be concatenated to make one large master
            
    """

    try:
        html_str = load_html(
            url=url,
            wdriver=wdriver,
            wait_time=wait_time
        )

        # bs list of all menu item parent elements
        menu_els: Bs = Bs(html_str, 'html.parser').find_all(attrs=itm_avd)
        
        # scroll down
        # ===========
        # zoom out to smallest
        wdriver.execute_script('document.body.style.zoom = "25%"')

        # scroll to capture moremenu elements
        scroll: ActionChains = ActionChains(wdriver).send_keys(Keys.PAGE_DOWN)
        # wait times for pgdown and to wait for html to load
        scroll_wt = 0.15

        # number of times to pgdown before loading html in each loop,
        # must be 1 or more
        pre_scrolls = 1
        # now set to 1 with the extreme zoom out, one pgdn at a time

        # setup break condition vars
        a = 0
        last_a = -1

        while True:
            # scroll down first time
            scroll.perform()

            for i in range(pre_scrolls - 1):
                sleep(scroll_wt)
                scroll.perform()

            # get current y (vert scroll) offset
            a = wdriver.execute_script("return window.scrollY")

            # if there's been no more scrolling since last time, we're done
            if last_a == a: break

            # get html_str again, more has loaded since scrolling

            more_html_str = load_html(
                url=url,
                wdriver=wdriver,
                wait_time=(wait_time / 2),
                load_anew=False
            )
            # soup new html str
            more_menu_els = Bs(more_html_str, 'html.parser').find_all(attrs=itm_avd)
            [menu_els.append(el) for el in more_menu_els]

            # reset last_a for next loop
            last_a = a


        logger.debug(f"Menu elements: {len(menu_els)}")

        # loop through each element in menu_els
        ser_list=[]
        for idx, i in enumerate(menu_els):
            try:
                i_ser = ser_item_details(
                    i_el=i,
                    itm_id_a=itm_id_a,
                    itm_price_avd=itm_price_avd,
                    itm_nm_avd=itm_nm_avd,
                    itm_de_avd=itm_de_avd,
                    cols=cols
                )
                ser_list.append(i_ser)

            except Exception:
                logger.error(f"Somethind went wrong on menu element {idx} from {url}")

        # results to dataframe
        df = Df(ser_list).drop_duplicates(subset=idcol).reset_index(drop=True)
        # set a column store_id will be foreign key for each store
        df['store_id']=store_id

        return df

    except KeyboardInterrupt:
        raise KeyboardInterrupt(
            " gh_scr.rest_menu_scrape_n_scroll: KeyboardInterrupt detected...")
    except Exception:
        logger.error(f"There was an an exception in rest_menu_scrape with {url}")



# details default values:
# ====================
# bs.find() keys
det_attrs = config_args['menu_scr_attrs']
# column head names for results
det_col_hds = config_args['det_scr_col_hds']

# menu item attribute and value
det_main_avd = det_attrs['about_par_avd']
det_name_avd = det_attrs['name_about_avd']
det_cuis_avd = det_attrs['rest_cuisines_avd']
det_flsch_lnk_avd = det_attrs['flsch_lnk_avd']
det_schdays_avd = det_attrs['schdays_avd']
det_schhoursPU_avd = det_attrs['schhoursPU_avd']
det_schhoursD_avd = det_attrs['schhoursD_avd']
det_phone_avd = det_attrs['phone_avd']
det_phone_a = det_attrs['phone_a']
det_map_avd = det_attrs['map_avd']
det_address_avd = det_attrs['address_avd']
det_contact_par_cs = det_attrs['contact_par_cs']

# names of series/df columns
det_sch_c = det_col_hds['sch']
det_ph_c = det_col_hds['phone']
det_lat_c = det_col_hds['lat']
det_lng_c = det_col_hds['lng']
det_mapurl_c = det_col_hds['map_url']
det_add_c = det_col_hds['address']
det_id_c = det_col_hds['id']
det_cuis_c = det_col_hds['cuis']

det_wait_time = float(config_args['menu_scr_wait_time'])

# ordered to apply to series, idcol and nmcol are loaded before the store scrape fn
det_cols = (det_sch_c, det_cuis_c, det_ph_c, det_lat_c, det_lng_c, det_mapurl_c, det_add_c, det_id_c, st_nmcol)

def rest_details_scrape(
    url: str,
    store_id: int,
    store_name: str,
    wdriver: webdriver.Chrome,
    wait_time: float = det_wait_time,
    det_main_avd: dict = det_main_avd,
    flsch_lnk_avd: dict=det_flsch_lnk_avd,
    cuis_avd: dict=det_cuis_avd,
    phone_avd: dict=det_phone_avd,
    phone_a: str=det_phone_a,
    map_el_avd: dict=det_map_avd,
    address_avd: dict=det_address_avd,
    cols: tuple = det_cols
) -> Ser:

    try:
        # get page and expand full schedule
        # wdriver.get(url)
        # sleep(wait_time)
        # scroll_end(wdriver)

        # # eff the schedule for now
        # # find and click link to expand full schedule
        # wait_for_fn = lambda wd: wd.find_element_by_xpath(
        #     '//*[@id="ghs-restaurant-about"]/div/div[3]/div[2]/span/div/div[2]')
        # exp_schd_toclick: WebElement = load_html(url, wdriver=wdriver, wait_for_fn=wait_for_fn, load_anew=False)
        # wdriver.execute_script("arguments[0].scrollIntoView(true)", exp_schd_toclick)
        # exp_schd_toclick.click()

        html_str = load_html(url=url, wdriver=wdriver, wait_time=wait_time)
        logger.debug(f"HTML extracted: {len(html_str)}")

        # get soup of 
        det_el: Tag = Bs(html_str, 'html.parser').find('span', attrs=det_main_avd)
        if not det_el:
            logger.error(f"About tag not found for {url}")
            return
        del html_str
        logger.debug(f"About Tag Descendents: {det_el}")


        # # get schedule strings
        # sch_str: str = ''
        # for i in range(1, 8):
        #     pass

        # get basic strings from basic elements with good attribute locators
        try:
            cuis = det_el.find('div', attrs=cuis_avd).text.split(', ')
        except Exception:
            cuis = pd.NA
        logger.debug(f"cuis: {cuis}")
        name = store_name
        logger.debug(f"name: {name}")
        try:
            phone = det_el.find('button', attrs=phone_avd).attrs[phone_a]
        except Exception:
            phone = pd.NA
        logger.debug(f"phone: {phone}")
        try:
            addr = det_el.find(attrs=address_avd).text
        except Exception:
            addr = pd.NA
        logger.debug(f"addr: {addr}")
        # get lat/lng and google maps link from parsed map_el style attribute 
        # ===================================================================
        map_el: Tag = det_el.find(attrs=map_el_avd)
        
        # get google maps link
        logger.debug(f"map_el.attrs: {map_el.attrs}")
        try:
            gmaplnk = map_el.attrs['href']
        except Exception:
            gmaplnk = pd.NA
        logger.debug(f"gmaplnk: {gmaplnk}")
        try:
            map_style = map_el.find('span').attrs['style']
        except Exception:
            map_style = pd.NA
        logger.debug(f"map_style: {map_style}")
        # parse map style attr to get lat/lng:
        #   split at parameter= right before the value, work on last element/second half
        #   split all param=args off, keep first element which is now just a string of <lat,lng>
        #   split that string into two elements and keep in tuple
        #   convert strings to floats
        try:
            lat_lng = tuple(\
            map_style.split('&center=')[-1]\
            .split('&')[0]\
            .split(',')
            )
            lat_lng = tuple([float(s) for s in lat_lng])
            # final values
            lat = lat_lng[0]
            lng = lat_lng[1]
        except Exception:
            lat, lng = pd.NA, pd.NA
        logger.debug(f"lat: {lat}")
        logger.debug(f"lng: {lng}")
        # ==============

        # schedule, 'cusines', phone number, lat, lng, google map link, address, grubhub id
        return Ser((pd.NA, cuis, phone, lat, lng, gmaplnk, addr, store_id, name), index=cols)

    except KeyboardInterrupt:
        raise KeyboardInterrupt(
            f" KeyboardIterrupt detected...{url}")
    except Exception:
        logger.error(
            f" There was an an exception with {url}")


test_url = "https://www.grubhub.com/restaurant/taza-cafe-176-n-franklin-st-chicago/266029"
test_store_id = 266029

def test_menu_scrape(url: str = test_url, store_id: int = test_store_id):
    try:
        return rest_menu_scrape(url, store_id)
    except:
        logging.error("Oops")


def test_det_scrape(url: str=test_url, store_id: int=test_store_id):
    try:
        return rest_details_scrape(url, store_id)
    except:
        logging.error("Oops")

# run to test menu scrape
if __name__ == '__main__':
    pass