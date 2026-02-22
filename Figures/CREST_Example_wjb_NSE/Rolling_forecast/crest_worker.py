# crest_worker.py
import os, stat, shutil
import numpy as np
import pandas as pd
import xarray as xr

def run_crest_multiprocess(args):
    iens, cfg_pack = args

    # 从 cfg_pack 取出你需要的所有变量
    fcst_data_type = cfg_pack["fcst_data_type"]
    issuetime = cfg_pack["issuetime"]
    warm_up_arange = cfg_pack["warm_up_arange"]
    rolling_result_output = cfg_pack["rolling_result_output"]
    # ... 以及你原函数用到的其它内容（header, dem_csv, x_ncols_list 等）

    # 然后把你原来 run_crest_multiprocess 的函数体粘进来
    # （把原来直接引用全局变量的地方，改成从 cfg_pack 里取）

    return