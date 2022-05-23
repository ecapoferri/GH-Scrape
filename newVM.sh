# !/bin/bash
# newVM.sh <new env name> <miniconda script name.sh> <miniconda url without script filename/>\

# sudo echo "<USER>  ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/<USER>

chrdr_path='https://chromedriver.storage.googleapis.com/101.0.4951.41/'
chrdr_fn='chromedriver_linux64'

mcnd_path='https://repo.anaconda.com/miniconda/'
mcnd_fn='Miniconda3-py39_4.11.0-Linux-x86_64.sh'

chr_path='https://dl.google.com/linux/direct/'
chr_fn'google-chrome-stable_current_amd64.deb'

mc_env='mydevenv'

sudo timedatectl set-timezone America/Chicago

mkdir dev && mkdir dev/python;

sudo apt update -y && sudo apt upgrade -y && sudo apt install -y\
	wget\
	xvfb\
	ssh\
	git;

sudo apt update -y && sudo apt upgrade -y;

# google chrome debian package
wget "$chr_path$chr_fn" && sudo apt install -y "./$chr_fn" && rm -rf "./$chr_fn";

# <chromedriver url/><same as chromedriver executable minus '.zip'>
wget "$chrdr_path$chrdr_fn.zip" && \
	gzip -d -S .zip "$chrdr_fn.zip" && \
	chmod +x "$chrdr_fn" && \
	mv "$chrdr_fn" "dev/$chrdr_fn.exe"; # exe to match path on local pc

wget "$mcnd_path$mcnd_fn" # <miniconda url/><same as miniconda script>
chmod +x "$mcnd_fn"
bash "./$mcnd_fn" # <miniconda script>
rm -rf "$mcnd_fn"
source ~/.bashrc

conda update -y conda
conda update -y --all
conda create -y --name "$mc_env"
conda activate -y --name  "$mc_env"
conda install -y -n "$mc_env" -c conda-forge\
	geopandas\
	autopep8\
	pip\
	selenium\
	jupyter\
	fastapi\
	requests\
	uvicorn\


conda upgrade -y -n "$mc_env" -c conda-forge --all
source ~/.bashrc