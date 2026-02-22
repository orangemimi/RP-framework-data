# @Time: 2022/7/25
# @Author: HeYuanqing
import math
import struct
import os
from osgeo import gdal
import numpy as np
import xarray as xr
import netCDF4 as nc
import matplotlib.pyplot as plt


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def readXajBinaryFile(path):
    binfile = open(path, 'rb')
    size = os.path.getsize(path)
    for i in range(size):
        data = binfile.read(1)
        print(data)
    binfile.close()


def readNcData(filePath):
    data = xr.open_dataset(filePath)
    print("ok")


def project_replace(nInputs, inputNames, inputData, file_project, file_project_replace):
    infile = open(file_project, "r")
    outfile = open(file_project_replace, "w")
    while 1:
        lineIn = infile.readline()
        if lineIn == "":
            break
        newLine = lineIn

        for fInd in range(nInputs):
            sInd_0 = newLine.find(inputNames[fInd])
            if sInd_0 < 0:
                continue
            newline_split = newLine.split()
            sInd = newLine.find(newline_split[2])
            sdata = inputData[fInd]
            strdata = str(sdata)
            lineTemp = newLine[0:sInd] + strdata + " " + "\n"
            newLine = lineTemp
        outfile.write(newLine)
    infile.close()
    outfile.close()
    os.remove(file_project)
    os.rename(file_project_replace, file_project)
    return


def readAscHead(ascPath):
    import codecs
    import numpy as np
    import pandas as pd
    # 读取dem的asc文件,输出头文件
    with codecs.open(ascPath, encoding='utf-8-sig') as f:
        ncols = int(f.readline()[14:].strip('\r\n'))
        nrows = int(f.readline()[14:].strip('\r\n'))
        xllcorner = float(f.readline()[14:].strip('\r\n'))
        yllcorner = float(f.readline()[14:].strip('\r\n'))
        cellsize = float(f.readline()[14:].strip('\r\n'))
        NODATA_value = int(f.readline()[14:].strip('\r\n'))
        # dem_csv = pd.read_csv(f, delimiter=' ', header=None).iloc[:, :ncols].to_numpy()

    return [ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value]


# 修改crestProject文件内的参数
def project_replace(InputLength, inputNames, inputData, file_project, file_project_replace):
    infile = open(file_project, "r")
    outfile = open(file_project_replace, "w")
    while 1:
        lineIn = infile.readline()
        if lineIn == "":
            break
        newLine = lineIn

        for fInd in range(InputLength):
            sInd_0 = newLine.find(inputNames[fInd])
            if sInd_0 < 0:
                continue
            newline_split = newLine.split()
            sInd = newLine.find(newline_split[2])
            sdata = inputData[fInd]
            strdata = str(sdata)
            lineTemp = newLine[0:sInd] + strdata + " " + "\n"
            newLine = lineTemp
        outfile.write(newLine)
    infile.close()
    outfile.close()
    # os.remove(file_project)
    # os.rename(file_project_replace, file_project)
    return


def writetiff(arr, raster_file, prj=None, trans=None):
    from osgeo import gdal
    import math
    """
    将数组转成栅格文件写入硬盘
    :param arr: 输入的mask数组 ReadAsArray()
    :param raster_file: 输出的栅格文件路径
    :param prj: gdal读取的投影信息 GetProjection()，默认为空
    :param trans: gdal读取的几何信息 (LonMin, LonCell_Size, 0, LatMax, 0, -LatCell_Size)，默认为空
    :return:
    """
    driver = gdal.GetDriverByName('GTiff')
    # arr = np.random.randint(0, 255, size=(200, 200, 1))
    im_height, im_width = arr.shape
    dst_ds = driver.Create(raster_file, im_width, im_height, 1, gdal.GDT_Float32)

    if prj:
        dst_ds.SetProjection(prj)
    if trans:
        dst_ds.SetGeoTransform(trans)

    # 将数组的各通道写入图片
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if math.isnan(arr[i, j]):
                arr[i, j] = 9999
    dst_ds.GetRasterBand(1).SetNoDataValue(9999)

    dst_ds.GetRasterBand(1).WriteArray(arr[:, :])

    dst_ds.FlushCache()
    dst_ds = None
    print("successfully convert array to raster")


def readWindNC(filePath):  # 读取宁亮老师风场数据并处理，以进行可视化
    import time
    import datetime

    # test
    from osgeo import gdal
    # arr = np.random.randint(0, 255, size=(200, 200, 1))
    src_ras_file = r"F:\个人资料\数据资料\ChinaData\ChinaDEM30m\江苏\ASTGTM2_N30E119_dem.tif"  # 提供地理坐标信息和几何信息的栅格底图
    # dataset = gdal.Open(src_ras_file)
    # projection = dataset.GetProjection()
    # transform = dataset.GetGeoTransform()
    data_name = 'ua'  # ['va', 'ua']
    data = xr.open_dataset(filePath)['ua']
    # data = xr.open_dataset(filePath)
    dates = data['time'].values
    lon = data['lon'].values
    lat = data['lat'].values
    values = data.values
    for i in range(len(dates)):
        value = values[i]
        date = dates[i]
        date_new = time.gmtime((date - np.datetime64('1970-01-01T00:00:00')) / np.timedelta64(1, 's'))
        saveFileName = str(date_new.tm_year) + '%02d' % int(date_new.tm_mon) + '%02d' % int(
            date_new.tm_mday) + '%02d' % int(date_new.tm_hour)
        raster_file = 'F:/' + saveFileName + 'ua.tif'  # 输出的栅格文件路径
        # raster_file = "G:\\数据\\宁亮老师-2017年气候模拟数据\\uv分量\\" + saveFileName + 'va.tif'  # 输出的栅格文件路径
        # un_time = time.mktime(date.timetuple())
        # print(un_time)
        # 将unix时间戳转换为“当前时间”格式
        # times = datetime.datetime.fromtimestamp(un_time)
        projection = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AXIS["Latitude",NORTH],AXIS["Longitude",EAST],AUTHORITY["EPSG","4326"]]'
        transform = (lon.min(), 0.25, 0, lat.max(), 0, -0.25)

        writetiff(value, raster_file, prj=projection, trans=transform)

    print("debugOK")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # data = xr.open_dataset(r"D:\Tencent\QQ\FileRecv\r_ts_2017_025.nc")
    #
    # data_pr = data['ts']
    # plt.contourf(data_pr['lon'],data_pr['lat'],data_pr.values[60,:,:])
    # plt.xlabel('lon')
    # plt.ylabel('lat')
    # plt.colorbar()
    # plt.show()
    # 释放内存。如果不释放，在arcgis或envi中打开该图像时显示文件已被占用
    # 宁亮老师数据处理
    readWindNC(r"G:\数据\宁亮老师-2017年气候模拟数据\2017气象数据\r_uva_2017_025.nc")

    # # 1. 流域头文件信息读取
    # ascHeadInfo = readAscHead("E:\\models\\CREST_Example\\Basics\\DEM.asc")
    # # [ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value]
    # ncols = ascHeadInfo[0]
    # nrows = ascHeadInfo[1]
    # xllcorner = ascHeadInfo[2]
    # yllcorner = ascHeadInfo[3]
    # cellsize = ascHeadInfo[4]
    # NODATA_value = ascHeadInfo[5]
    # # 2. 输入参数信息读取
    # TimeMark = 'd'
    # TimeStep = '1'
    # StartDate = '20090722'
    # WarmupDate = '20100722'
    # EndDate = '20100731'
    #
    # OutletName = 'wjb'
    # OutletLong = '115.612365'
    # OutletLati = '32.429253'
    #
    # OutPixName1 = OutletName
    # OutPixLong1 = OutletLong
    # OutPixLati1 = OutletLati
    #
    # inputNames = ['NCols', 'NRows', 'XLLCorner', 'YLLCorner', 'CellSize', 'NoData_value', 'TimeMark', 'TimeStep',
    #               'StartDate', 'WarmupDate', 'EndDate', 'OutletName', 'OutletLong', 'OutletLati', 'OutPixName1',
    #               'OutPixLong1', 'OutPixLati1']
    #
    # inputData = [ncols, nrows, xllcorner, yllcorner, cellsize, NODATA_value, TimeMark, TimeStep, StartDate, WarmupDate,
    #              EndDate, OutletName, OutletLong, OutletLati, OutPixName1, OutPixLong1, OutPixLati1]
    # configFile_ori = "E:\\models\\CREST_Example\\IdealExample_Windows_edit.Project"
    # configFile_replace = "E:\\models\\CREST_Example\\IdealExample_Windows.Project"
    # project_replace(len(inputNames), inputNames, inputData, configFile_ori, configFile_replace)

# readXajBinaryFile(r"E:\working\HHU_NNU\Program\HydroModelExe\XAJ\force\Evp_2013-1-1-0~2013-10-31-0_24-backup.bin")
# readNcData(r"E:\working\HHU_NNU\Program\CREST_Example_wjb_NSE\Rolling_result\20100722\raw_forecast\ens_0.nc")
# print_hi('PyCharm')


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
