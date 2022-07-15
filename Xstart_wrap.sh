# ./start_wrap.sh INDEX_TO_START <1_TO_RESET_LOG_FILES | 0_TO_APPEND> SCRIPT_CHOICE SCRAPE_ITERATION_INDEX SCRIPT_PATH
# env var for scrape iteration index for dir and file names
# export GHSCRITER="99"
# create cache directory if it doesn't exist
# python seems to have issues creating directories implicitly sometimes?
if [ ! -d OUTPUT/99-menu_cache &> /dev/null ]; then
	mkdir OUTPUT/99-menu_cache
fi
# executes command within xvfb, appending (in case they have already been started)
# stderr/out to error log file
xvfb-run pythonsh gh_scr_StorePages.py 0 1 "details" > OUTPUT/gh_scr_DETAILS-ERROR-99.log 2>&1
