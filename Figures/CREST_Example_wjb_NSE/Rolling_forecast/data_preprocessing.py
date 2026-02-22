import xarray as xr
import pandas as pd

# 处理不同类型的预报数据,包括原始预报以及BJP后处理后的预报
# 目的：将观测数据与预报数据拼接起来,观测在前，预报在后
def raw_fcst_processing(iens, issuetime, observation, raw_forecast, x_ncols_list, y_nrows_list, warm_up_arange):

    """ 
    输入数据包括
    issuetime,预报发布日,数据格式如'2008-01-01'
    observation,观测数据,示例变量名:维度信息,'pre':date*lat*lon
    raw_forecast,原始预报数据,示例变量名:维度信息,'tp':issuetime*ens*leadtime*lat*lon
    x_ncols_list:根据DEM读取的流域的经度序列
    y_nrows_list:根据DEM读取的流域的纬度序列
    warm_up_arange:crest模型预热期时长,数据格式如'1y','1m','1d',分别表示1年、1月、1日
    """
    obs_ = xr.open_dataset(observation)
    ens_ = xr.open_dataset(raw_forecast)
    lead = ens_.leadtime.to_numpy()

    # 表示预报发布日
    issuetime = pd.to_datetime(issuetime) # 转变预报发布日数据类型为DatetimeIndex

    if warm_up_arange[-1] == 'y':
        warm_up_start = issuetime - pd.DateOffset(years=int(warm_up_arange[:-1]))
    elif warm_up_arange[-1] == 'm':
        warm_up_start = issuetime - pd.DateOffset(months=int(warm_up_arange[:-1]))
    else:
        warm_up_start = issuetime - pd.DateOffset(days=int(warm_up_arange[:-1]))

    # 计算预热期,示例中定为1年,存放观测数据
    warm_up_range = pd.date_range(start = warm_up_start, end = issuetime - pd.DateOffset(days=1))
    # 计算预报验证期,预报发布日对应的预见期1天-10天
    validtime_range = pd.date_range(start= issuetime, end = issuetime + pd.DateOffset(days = len(lead)-1))
    
    # 截取预热期观测值,并插值成王家坝流域范围,统一经纬度便于拼接
    obs_select = obs_.sel(date=warm_up_range)
    obs_select = obs_select.interp(lat=y_nrows_list,lon=x_ncols_list)
    # 截取原始预报发布日预报值，对原始预报变量名进行重命名，便于拼接
    ens_select = ens_.sel(issuetime = issuetime)
    ens_select = ens_select.interp(lat=y_nrows_list,lon=x_ncols_list)
    ens_select = ens_select.rename_vars({'tp':'pre'})
    # 对原始预报维度leadtime进行重命名,并表示为预报验证期:预报发布日对应的预见期1天-10天,表示从预报日算起的10天预报数据
    ens_select = ens_select.rename({"leadtime":"date"})
    ens_select['date'] = validtime_range

    combine_time = None # 按照时间进行拼接
    combine_time = xr.concat([obs_select,ens_select.sel(ens=iens)],dim='date') #将观测数据与某集合成员对应的预报数据按照时间序列拼接在一起

    # 函数输出：shape:ens*lon*lat*date
    return combine_time,warm_up_range,validtime_range,lead

def BJP_fcst_processing(iens,issuetime, observation, BJP_forecast, x_ncols_list, y_nrows_list, warm_up_arange):
    """ 
    输入数据包括
    issuetime,预报发布日,数据格式如'2008-01-01'
    observation,观测数据,示例变量名:维度信息,'pre':date*lat*lon
    BJP_forecast,后处理后的预报数据,示例变量名:维度信息,'__xarray_dataarray_variable__':validdate*ens*leadtime*lat*lon
    x_ncols_list:根据DEM读取的流域的经度
    y_nrows_list:根据DEM读取的流域的纬度
    warm_up_arange:crest模型预热期时长,数据格式如'1y','1m','1d',分别表示1年、1月、1日
    """
    obs_ = xr.open_dataset(observation)
    ens_ = xr.open_dataset(BJP_forecast)
    lead = ens_.leadtime.to_numpy()

    # 表示预报发布时间历时
    issuetime = pd.to_datetime(issuetime) # 转变数据类型为DatetimeIndex

    if warm_up_arange[-1] == 'y':
        warm_up_start = issuetime - pd.DateOffset(years=int(warm_up_arange[:-1]))
    elif warm_up_arange[-1] == 'm':
        warm_up_start = issuetime - pd.DateOffset(months=int(warm_up_arange[:-1]))
    else:
        warm_up_start = issuetime - pd.DateOffset(days=int(warm_up_arange[:-1]))

    # 计算预热期,此处为1年,存放观测数据
    warm_up_range = pd.date_range(start = warm_up_start, end = issuetime - pd.DateOffset(days=1))
    # 计算预报验证期,预报发布日对应的预见期1天-7天
    validtime_range = pd.date_range(start= issuetime, end = issuetime + pd.DateOffset(days = len(lead)-1))
    
    # 截取预热期观测值,并插值成王家坝流域范围,统一经纬度便于拼接
    obs_select = obs_.sel(date=warm_up_range)
    obs_select = obs_select.interp(lat=y_nrows_list,lon=x_ncols_list)
    # 截取后处理后的预报发布日预报值，对后处理后的预报变量名进行重命名，便于拼接
    ens_select = ens_.sel(validdate = issuetime)
    ens_select = ens_select.interp(lat=y_nrows_list,lon=x_ncols_list)
    ens_select = ens_select.rename_vars({'__xarray_dataarray_variable__':'pre'})
    # 对后处理后的预报维度leadtime进行重命名,并表示为预报验证期:预报发布日对应的预见期1天-7天,表示从预报日算起的7天预报数据
    ens_select = ens_select.rename({"leadtime":"date"})
    ens_select['date'] = validtime_range

    combine_time = None # 按照时间进行拼接
    combine_time = xr.concat([obs_select,ens_select.sel(ens=iens)],dim='date') #将观测数据与某集合成员对应的预报数据按照时间序列拼接在一起
    
    return combine_time,warm_up_range,validtime_range,lead



