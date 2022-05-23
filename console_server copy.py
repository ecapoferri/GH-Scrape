from fastapi import FastAPI
from time import sleep
from os import environ


console_path = environ['GHSCR_CONS_PATH']

# size of line block, or start line
app = FastAPI()

@app.get("/")
async def root():
	return {"message": "Hello World"}

@app.get("/scrape-console")
async def scrape_console():
	block_st = -100
	with open(console_path, 'r') as f:
		lines = f.readlines()

	# Clean up lines
	block = lines[block_st:]
	# line number key
	l_num = [ i for i in range(-block_st)]
	# dict'ize
	return {k: v for k, v in zip(l_num, block)}
