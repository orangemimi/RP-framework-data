import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import json
import os


def draw_1():
    # 读取.json格式文件的内容
    with open('cfg_crest.json', 'r+') as file:
        content = file.read()
    cfg = json.loads(content)

    issuetime = cfg['issuetime']
    runoff_obs_begin = cfg['runoff_obs_begin']
    runoff_obs_end = cfg['runoff_obs_end']
    file_Outlet_wjb_Results = cfg['file_Outlet_wjb_Results']
    fcst_data_type = cfg['fcst_data_type']
    rolling_result_output = cfg['rolling_result_output']
    file_path = cfg['file_path']
    streamflow_start = cfg['streamflow_start']
    streamflow_end = cfg['streamflow_end']

    Rolling_result_path = rolling_result_output + '*.nc'
    rolling_fcst = xr.open_mfdataset(Rolling_result_path)
    print(rolling_fcst)

    rolling_fcst_all = rolling_result_output + 'all/'
    if not os.path.exists(rolling_fcst_all):
        os.mkdir(rolling_fcst_all)

    rolling_fcst.to_netcdf(rolling_fcst_all + 'rolling_fcst_ens.nc')

    ens = rolling_fcst.ens.to_numpy()
    issuetime = pd.to_datetime(rolling_fcst.issuetime)
    lead = rolling_fcst.lead.to_numpy()
    nlead = len(lead)

    fig, axes = plt.subplots(1, 1, figsize=(15, 12))

    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['savefig.dpi'] = 600  # 图片像素
    plt.rcParams['figure.dpi'] = 600

    font1 = {'family': 'SimSun', 'weight': 'normal', 'size': 22}
    font2 = {'family': 'Times New Roman', 'weight': 'normal', 'size': 24}  # 设置字体模板，
    font3 = {'family': 'SimSun', 'weight': 'normal', 'size': 22}

    # 设置x轴
    plt.tick_params( \
        axis='x',  # 设置x轴
        direction='in',  # 小坐标方向，in、out
        which='major',  # 主标尺和小标尺一起显示，major、minor、both
        bottom=True,  # 底部标尺打开
        top=False,  # 上部标尺关闭
        labelbottom=True,  # x轴标签打开
        labelsize=20)  # x轴标签大小
    plt.tick_params( \
        axis='y',
        direction='in',
        which='both',
        left=True,
        right=False,
        labelbottom=True,
        labelsize=20)
    # plt.minorticks_on()#开启小坐标
    plt.ticklabel_format(axis='both', style='sci')  # sci文章的风格

    cali_start = issuetime[0].strftime('%Y%m%d')
    cali_end = issuetime + pd.DateOffset(days=int(nlead) - 1)
    cali_end = cali_end[0].strftime('%Y%m%d')

    cali_date = pd.date_range(start=cali_start, end=cali_end)

    obs_date_list = pd.date_range(start=runoff_obs_begin, end=runoff_obs_end)
    obs_date_streamflow = pd.date_range(start=streamflow_start,
                                        end=((issuetime - pd.DateOffset(days=1))[0].strftime('%Y%m%d')))

    result = pd.read_csv(file_Outlet_wjb_Results, usecols=['R', 'RObs']).values
    result_df = pd.DataFrame(result, index=obs_date_list, columns=['R', 'RObs'])

    result_df_select = result_df.loc[obs_date_streamflow].to_numpy()

    Qobs = result_df_select[:, 1]
    Qsim = result_df_select[:, 0]

    rolling_fcst_median = np.median(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), axis=0)
    rolling_fcst_prct5 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 5, axis=0)
    rolling_fcst_prct95 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 95, axis=0)
    rolling_fcst_prct25 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 25, axis=0)
    rolling_fcst_prct75 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 75, axis=0)

    axes.fill_between(cali_date, rolling_fcst_prct5, rolling_fcst_prct95, color='darkcyan', alpha=0.75, linewidth=0,
                      label='5%-95%')
    axes.fill_between(cali_date, rolling_fcst_prct25, rolling_fcst_prct75, color='greenyellow', alpha=0.75, linewidth=0,
                      label='25%-75%')
    axes.plot(obs_date_streamflow, Qobs, 'r-', lw=2, label='observated streamflow')
    axes.plot(obs_date_streamflow, Qsim, 'k-', lw=2, label='simulated streamflow')
    axes.plot(cali_date, rolling_fcst_median, 'b-', lw=2, label='forecast ensemble median')

    tick_index = pd.date_range(start=streamflow_start, end=streamflow_end, freq="7D")
    fig.legend(loc='upper left', bbox_to_anchor=(0.6, 0.8), shadow=False, prop=font2)
    plt.xticks(tick_index)

    plt.savefig(rolling_result_output + cfg['issuetime'] + '_' + str(fcst_data_type) + '_type1' + '.png',
                bbox_inches="tight")

    return


def draw_2():
    # 读取.json格式文件的内容
    with open('cfg_crest.json', 'r+') as file:
        content = file.read()
    cfg = json.loads(content)

    issuetime = cfg['issuetime']
    runoff_obs_begin = cfg['runoff_obs_begin']
    runoff_obs_end = cfg['runoff_obs_end']
    file_Outlet_wjb_Results = cfg['file_Outlet_wjb_Results']
    fcst_data_type = cfg['fcst_data_type']
    rolling_result_output = cfg['rolling_result_output']
    file_path = cfg['file_path']
    streamflow_start = cfg['streamflow_start']
    streamflow_end = cfg['streamflow_end']

    Rolling_result_path = rolling_result_output + '*.nc'
    rolling_fcst = xr.open_mfdataset(Rolling_result_path)
    print(rolling_fcst)

    rolling_fcst_all = rolling_result_output + 'all/'
    if not os.path.exists(rolling_fcst_all):
        os.mkdir(rolling_fcst_all)

    rolling_fcst.to_netcdf(rolling_fcst_all + 'rolling_fcst_ens.nc')

    ens = rolling_fcst.ens.to_numpy()
    issuetime = pd.to_datetime(rolling_fcst.issuetime)
    lead = rolling_fcst.lead.to_numpy()
    nlead = len(lead)

    fig, axes = plt.subplots(1, 1, figsize=(15, 12))

    plt.rcParams['font.sans-serif'] = ['Times New Roman']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['savefig.dpi'] = 600  # 图片像素
    plt.rcParams['figure.dpi'] = 600

    font1 = {'family': 'SimSun', 'weight': 'normal', 'size': 22}
    font2 = {'family': 'Times New Roman', 'weight': 'normal', 'size': 24}  # 设置字体模板，
    font3 = {'family': 'SimSun', 'weight': 'normal', 'size': 22}

    # 设置x轴
    plt.tick_params( \
        axis='x',  # 设置x轴
        direction='in',  # 小坐标方向，in、out
        which='major',  # 主标尺和小标尺一起显示，major、minor、both
        bottom=True,  # 底部标尺打开
        top=False,  # 上部标尺关闭
        labelbottom=True,  # x轴标签打开
        labelsize=20)  # x轴标签大小
    plt.tick_params( \
        axis='y',
        direction='in',
        which='both',
        left=True,
        right=False,
        labelbottom=True,
        labelsize=20)
    # plt.minorticks_on()#开启小坐标
    plt.ticklabel_format(axis='both', style='sci')  # sci文章的风格

    cali_start = issuetime[0].strftime('%Y%m%d')
    cali_end = issuetime + pd.DateOffset(days=int(nlead) - 1)
    cali_end = cali_end[0].strftime('%Y%m%d')

    cali_date = pd.date_range(start=cali_start, end=cali_end)

    obs_date_list = pd.date_range(start=runoff_obs_begin, end=runoff_obs_end)
    obs_date_streamflow = pd.date_range(start=streamflow_start, end=streamflow_end)

    result = pd.read_csv(file_Outlet_wjb_Results, usecols=['R', 'RObs']).values
    result_df = pd.DataFrame(result, index=obs_date_list, columns=['R', 'RObs'])

    result_df_select = result_df.loc[obs_date_streamflow].to_numpy()

    Qobs = result_df_select[:, 1]
    Qsim = result_df_select[:, 0]

    rolling_fcst_median = np.median(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), axis=0)
    rolling_fcst_prct5 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 5, axis=0)
    rolling_fcst_prct95 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 95, axis=0)
    rolling_fcst_prct25 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 25, axis=0)
    rolling_fcst_prct75 = np.percentile(rolling_fcst['__xarray_dataarray_variable__'][0, :, :].to_numpy(), 75, axis=0)

    axes.fill_between(cali_date, rolling_fcst_prct5, rolling_fcst_prct95, color='darkcyan', alpha=0.75, linewidth=0,
                      label='5%-95%')
    axes.fill_between(cali_date, rolling_fcst_prct25, rolling_fcst_prct75, color='greenyellow', alpha=0.75, linewidth=0,
                      label='25%-75%')
    axes.plot(obs_date_streamflow, Qobs, 'r-', lw=2, label='observated streamflow')
    axes.plot(obs_date_streamflow, Qsim, 'k-', lw=2, label='simulated streamflow')
    axes.plot(cali_date, rolling_fcst_median, 'b-', lw=2, label='forecast ensemble median')

    tick_index = pd.date_range(start=streamflow_start, end=streamflow_end, freq="7D")
    fig.legend(loc='upper left', bbox_to_anchor=(0.6, 0.8), shadow=False, prop=font2)
    plt.xticks(tick_index)
    plt.savefig(rolling_result_output + cfg['issuetime'] + '_' + str(fcst_data_type) + '_type2' + '.png',
                bbox_inches="tight")

    return

if __name__ == '__main__':
    draw_1()