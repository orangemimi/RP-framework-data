import os

# 修改project文件内的参数
def project_replace(nInputs,inputNames,inputData,file_project,file_project_replace):
    infile = open(file_project, "r")
    outfile = open(file_project_replace, "w")
    while 1:
        lineIn  = infile.readline()
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
            lineTemp = newLine[0:sInd] + strdata +  " " + "\n"
            newLine = lineTemp
        outfile.write(newLine)
    infile.close()
    outfile.close()
    os.remove(file_project)
    os.rename(file_project_replace,file_project)
    return

# 调用exe/centos/ubuntu等文件,运行crest
def runApplication(modelFile):
    sysComm = modelFile
    os.system(sysComm)
    return