import os

import docs.source.make_envs_rst as make_envs_rst

make_envs_rst.main()
# Make html, can also be run in terminal
os.system('make html')
# Open the index page
os.system('open _build/html/index.html')
# Requires ngym_foraging and ngym_foraging.github.io to be in the same directory
os.system('cp -r ./_build/html/ ../../ngym_foraging.github.io')