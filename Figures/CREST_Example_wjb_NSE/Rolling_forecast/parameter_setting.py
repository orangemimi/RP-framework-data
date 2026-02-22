import json

cfg = {}

# 输入参数
cfg['warm_up_arange'] = '1y'  # 预热期时长,可输入'1y'、'1m'、'1d'三种以'y'、'm'、'd'格式结尾的字符串,分别表示1years,1months,1days
cfg['issuetime'] = '20100722'  # 滚动预报起报时刻(起报时间选在20100101-20101231之间)
cfg['runoff_obs_begin'] = '2008-01-01'  # 现有径流量观测值的起始时刻,用于画图
cfg['runoff_obs_end'] = '2016-12-31'  # 现有径流量观测值的终止时刻,用于画图
cfg['fcst_data_type'] = 'raw_forecast'  # 选填'raw_forecast'、'BJP_forecast'两种,分别表示对原始预报、BJP后处理后的预报进行滚动预报
cfg['n_process'] = 10  # 多少进程 # 参考:原始预报集合成员是5,后处理后集合成员为50

cfg['streamflow_start'] = '2010-07-09'  # 场次洪水开始时刻,作图用
cfg['streamflow_end'] = '2010-08-15'  # 场次洪水终止时刻,作图用
cfg['drawing_type'] = 'type2'  # 选填type1,type2; 1是起报时刻之前绘制观测径流、模拟径流,起报时刻起绘制集合径流预报; 2是绘制完整的场次观测径流、模拟径流;

# crest模型总文件夹存储路径
cfg['file_path'] = 'E:/working/HHU_NNU/Program/CREST_Example_wjb_NSE/'  # crest模型总文件夹存储路径

# 输入数据
cfg['file_dem'] = cfg['file_path'] + 'Basics/DEM.asc'  # 王家坝流域dem
cfg['file_obs01_input'] = cfg['file_path'] + 'Data/obs01_daily.nc'  # 滚动预报中用于预热的观测值
cfg['file_BJPfcst_input'] = cfg['file_path'] + 'Data/ens_gefs_bjp.nc'  # 滚动预报用于预报的BJP后处理后的预报
cfg['file_rawfcst_input'] = cfg['file_path'] + 'Data/ens_gefs_raw.nc'  # 滚动预报用于预报的原始预报

# 输出数据
cfg['rolling_result_output'] = cfg['file_path'] + 'Rolling_result/' + cfg['issuetime'] + '/' + cfg[
    'fcst_data_type'] + '/'  # 观测值与预报值合并后,逐成员输出逐日的Rains数据的总文件夹

# linux系统中,模型运行的关键文件:Linux.project文件以及centos文件
# 参数率定结束后,模拟期和验证期运行crest模型,检验模拟结果,便于在集合径流预报作图中显示模拟径流量
# 同时方便将project文件以及centos文件拷贝进逐集合成员的运行文件夹
cfg['file_Outlet_wjb_Results'] = cfg['file_path'] + 'Results/Outlet_wjb_Results.csv'  # crest模型模拟结果, wjb的csv文件：Outlet_wjb_Results.csv,用于画图
# # 在linux下,有ubuntu和centos两种
# cfg['file_project'] = cfg['file_path']  + 'IdealExample_Linux.Project' # crest模型的project文件,用于shutil.copyfile
# cfg['file_module'] = cfg['file_path']  + 'crest_v2_1.centos' # crest模型,用于shutil.copyfile
# cfg['file_module'] = cfg['file_path']  + 'crest_v2_1.ubuntu' # crest模型,用于shutil.copyfile

# 在windows下
cfg['file_project'] = cfg['file_path'] + 'IdealExample_Windows.Project'  # crest模型的project文件,用于shutil.copyfile
cfg['file_module'] = cfg['file_path'] + 'crest_v2_1.exe'  # crest模型,用于shutil.copyfile

# project文件内绝对路径的修改；其中RainPath、ResultPath在后续程序中命名(两者在并行输出时,绝对路径会改变)
cfg['BasicPath'] = '"' + cfg['file_path'] + 'Basics/' + '"'
cfg['ParamPath'] = '"' + cfg['file_path'] + 'Params/' + '"'
cfg['StatePath'] = '"' + cfg['file_path'] + 'States/' + '"'
cfg['ICSPath'] = '"' + cfg['file_path'] + 'ICS/' + '"'
cfg['PETPath'] = '"' + cfg['file_path'] + 'PETs/wjb.pet.' + '"'
cfg['CalibPath'] = '"' + cfg['file_path'] + 'Calibs/' + '"'
cfg['OBSPath'] = '"' + cfg['file_path'] + 'OBS/' + '"'
print(cfg)

# write cfg file
json_str = json.dumps(cfg)
with open('cfg_crest.json', 'w') as json_file:
    json_file.write(json_str)
