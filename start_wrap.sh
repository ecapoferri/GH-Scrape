# env var for scrape iteration index for dir and file names
export GHSCRITER=$2
# create cache directory if it doesn't exist
# python seems to have issues creating directories implicitly 
if [ ! `ls OUTPUT/$2-menu_cache &> /dev/null` ]
then
    mkdir OUTPUT/$2-menu_cache
fi
# executes command within xvfb, appending (in case they have already been started)
# stderr/out to Log file
xvfb-run\
    pythonsh\
        $3 $1 1 1>> OUTPUT/gh_scr_LOG-$2.log 2>> OUTPUT/gh_scr_LOG-$2.log