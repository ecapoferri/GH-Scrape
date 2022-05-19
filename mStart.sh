conda activate mydevenv

export GHSCRITER=$2

mkdir gh_scr/$2-menu_cache

xvfb-run\
    pythonsh\
        ./gh_scr_menuscrapenscroll.py $1 1\
            1>> gh_scr/gh_scr_LOG-$2.log\
            2>> gh_scr/gh_scr_LOG-$2.log\
&