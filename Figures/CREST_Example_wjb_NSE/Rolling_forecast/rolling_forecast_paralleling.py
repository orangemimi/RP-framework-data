import codecs
import json
import os, stat
import shutil

import numpy as np
import pandas as pd
import xarray as xr
import time
from run_crest import project_replace, runApplication
from data_preprocessing import raw_fcst_processing, BJP_fcst_processing
from rolling_fcst_drawing import draw_1, draw_2

print("Start......")
startTime = time.time()
print("Start  time：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(startTime)))
# 读取.json格式文件的内容
with open('cfg_crest.json', 'r+') as file:
    content = file.read()
cfg = json.loads(content)

# 文件夹总路径
file_path = cfg['file_path']
# 输入参数
warm_up_arange = cfg['warm_up_arange']  # 预热时长
issuetime = cfg['issuetime']  # 预报发布日
fcst_data_type = cfg['fcst_data_type']  # 预报数据类型:原始数据or后处理后的数据
n_process = cfg['n_process']  # 进程数
drawing_type = cfg['drawing_type']

# 输入数据路径
file_dem = cfg['file_dem']  # dem
file_obs01_input = cfg['file_obs01_input']  # 观测降水
file_BJPfcst_input = cfg['file_BJPfcst_input']  # 后处理后的降水预报
file_rawfcst_input = cfg['file_rawfcst_input']  # 原始降水预报

# 输出路径
rolling_result_output = cfg['rolling_result_output']
# project文件相关参数
file_project = cfg['file_project']
file_module = cfg['file_module']

BasicPath = cfg['BasicPath']
ParamPath = cfg['ParamPath']
StatePath = cfg['StatePath']
ICSPath = cfg['ICSPath']
PETPath = cfg['PETPath']
CalibPath = cfg['CalibPath']
OBSPath = cfg['OBSPath']

# 确定集合成员序列
if fcst_data_type == 'raw_forecast':
    member = xr.open_dataset(file_rawfcst_input).ens.to_numpy()
elif fcst_data_type == 'BJP_forecast':
    member = xr.open_dataset(file_BJPfcst_input).ens.to_numpy()

# 读取dem的asc文件,输出头文件
with codecs.open(file_dem, encoding='utf-8-sig') as f:
    ncols = int(f.readline()[14:].strip('\r\n'))
    nrows = int(f.readline()[14:].strip('\r\n'))
    xllcorner = float(f.readline()[14:].strip('\r\n'))
    yllcorner = float(f.readline()[14:].strip('\r\n'))
    cellsize = float(f.readline()[14:].strip('\r\n'))
    NODATA_value = int(f.readline()[14:].strip('\r\n'))
    dem_csv = pd.read_csv(f, delimiter=' ', header=None).iloc[:, :ncols].to_numpy()
# 计算出DEM所在asc文件的经纬度序列
x_ncols = np.arange(ncols)
y_nrows = np.arange(nrows)
x_ncols_list = xllcorner + cellsize * (x_ncols + 1 / 2)
y_nrows_list = yllcorner + cellsize * (nrows - y_nrows - 1 / 2)
# .asc头文件
header = "ncols            {}\r\n".format(ncols)
header += "nrows            {}\r\n".format(nrows)
header += "xllcorner        {}\r\n".format(xllcorner)
header += "yllcorner        {}\r\n".format(yllcorner)
header += "cellsize         {}\r\n".format(cellsize)
header += "NODATA_value     {}\r\n".format(NODATA_value)


def run_crest_multiprocess(iens):
    # 对原始预报/后处理后的预报进行数据处理
    if fcst_data_type == 'raw_forecast':
        fcst_processed, warm_up_range, validtime_range, lead = raw_fcst_processing(iens, issuetime, file_obs01_input,
                                                                                   file_rawfcst_input, x_ncols_list,
                                                                                   y_nrows_list, warm_up_arange)
    elif fcst_data_type == 'BJP_forecast':
        fcst_processed, warm_up_range, validtime_range, lead = BJP_fcst_processing(iens, issuetime, file_obs01_input,
                                                                                   file_BJPfcst_input, x_ncols_list,
                                                                                   y_nrows_list, warm_up_arange)

    # project内需要修改的StartDate、EndDate、WarmupDate对应的时间
    start = warm_up_range[0].strftime('%Y%m%d')
    End = validtime_range[-1].strftime('%Y%m%d')
    valid_start = validtime_range[0].strftime('%Y%m%d')
    warmup = valid_start

    # 逐集合成员输出Rains数据
    combine_interp = fcst_processed.transpose('date', 'lat', 'lon')
    date_range1 = pd.to_datetime(fcst_processed.date.to_numpy())

    rolling_fcst = np.zeros([1, 1, len(lead)])  # axis=0,存放issuetime,axis=1,存在集合成员

    iens_path = rolling_result_output + 'ens_' + str(iens) + '/'
    if not os.path.isdir(iens_path):
        os.makedirs(iens_path)  # 每个集合成员创建一个新的空的文件夹

    # 逐日数据输出Rains数据
    for iday in date_range1:
        time_daily = iday.strftime('%Y%m%d')
        combine_interp_daily = combine_interp.sel(date=time_daily)['pre'].values
        mean_value = np.nanmean(combine_interp_daily)
        combine_interp_daily[dem_csv == NODATA_value] = NODATA_value

        combine_interp_daily_df = pd.DataFrame(combine_interp_daily, index=y_nrows_list, columns=x_ncols_list)
        combine_interp_daily_df = combine_interp_daily_df.fillna(value=mean_value)

        file_output_path = iens_path + 'wjb.rain.' + time_daily + '.asc'
        with open(file_output_path, 'wb') as f:
            f.write(bytes(header, "UTF-8"))
            combine_interp_daily_df.to_csv(f, sep=' ', index=0, header=0)

    target_project = iens_path + 'IdealExample_Linux.Project'
    target_centos = iens_path + 'crest_v2_1.centos'
    shutil.copyfile(file_project, target_project)  # 将project、centos文件拷贝至每个集合成员所在的文件夹
    shutil.copyfile(file_module, target_centos)

    # 修改project文件
    # 修改project内的绝对路径,StartDate,WarmupDate,EndDate
    target_project_replace = iens_path + 'IdealExample_Linux_replace.Project'
    RainPath = '"' + iens_path + 'wjb.rain.' + '"'
    ResultPath = '"' + iens_path + 'Results/' + '"'

    result_path_create = iens_path + 'Results/'
    if not os.path.exists(result_path_create):
        os.mkdir(result_path_create)  # 在每个集合成员所在的文件夹内创建Results文件夹,存放运行结果

    inputNames = ['BasicPath', 'ParamPath', 'StatePath', 'ICSPath', 'RainPath', 'PETPath', 'ResultPath', 'CalibPath',
                  'OBSPath', 'StartDate', 'WarmupDate', 'EndDate']
    inputData = [BasicPath, ParamPath, StatePath, ICSPath, RainPath, PETPath, ResultPath, CalibPath, OBSPath, start,
                 warmup, End]
    nInputs = len(inputNames)
    project_replace(nInputs, inputNames, inputData, target_project, target_project_replace)

    # 调用centos文件进行程序运行
    # 修改linux下文件权限,使得文件拥有者具有读写执行的全部权限
    os.chmod(target_centos, stat.S_IRWXU)
    os.chmod(target_project, stat.S_IRWXU)

    modelFile = target_centos + ' ' + target_project

    runApplication(modelFile)

    # 读取result文件,存储预报发布日发布的预见期内的降水预报驱动crest模型获得的径流预报
    file_Outlet_wjb_Results = iens_path + 'Results/Outlet_wjb_Results.csv'
    result_date = pd.date_range(start=start, end=End)
    cali_date_1 = pd.date_range(start=valid_start, end=End)
    result = pd.read_csv(file_Outlet_wjb_Results, usecols=['R']).values
    result_df = pd.DataFrame(result, index=result_date, columns=['R'])
    result_df_select = result_df.loc[cali_date_1].to_numpy()
    Qsim = result_df_select[:, 0]
    rolling_fcst[0, 0, :] = Qsim

    # 存储滚动预报结果
    Rolling_result = rolling_result_output + 'ens_' + str(iens) + '.nc'

    rolling_fcst_dataarray = xr.DataArray(
        rolling_fcst,
        coords={
            "issuetime": pd.to_datetime([issuetime]),
            "ens": np.array([iens]),
            "lead": lead,
        },
        dims=["issuetime", "ens", "lead"],
    )
    # 逐集合成员保存滚动预报结果
    rolling_fcst_dataarray.to_netcdf(Rolling_result)
    return


from multiprocessing import Pool

if __name__ == '__main__':
    pool = Pool(n_process)
    jobs = np.arange(len(member))

    pool.map_async(run_crest_multiprocess, jobs)
    pool.close()
    pool.join()

    print("End")
    endTime = time.time()
    print("End time" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(endTime)))
    print('Consuming time' + str(endTime - startTime) + "seconds")

    if drawing_type == 'type1':
        draw_1()
    else:
        draw_2()
