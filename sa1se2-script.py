import re
import subprocess as sp
import pandas as pd
from pandas.core.indexes.base import Index
from os import listdir, pipe
from os.path import isfile, join
import json
import os


class ReadInputConfig:
    def __init__(self):
       pass
    def getInputConfig(self,configInputFilePath):
        print(configInputFilePath)
        with open(configInputFilePath) as configInput:
         print(configInput)
         configData= json.load(configInput)  
         return configData

class ExecuteCommand():
    def __init__(self):
        pass
    def executeCommand(self,command):
        print("Command",command)
        os.system(command)
        
        print("command sucessfully executed: "+command)
    def getCommandOutput(self,command):
        print("Command",command)
        output = sp.getoutput(command)
        print(output)
        return output
    def saveCommandOutput(self,output,ouputFilePath):
        with open(ouputFilePath,'w') as f:
            f.write(output)
        print("File Was saved succesfully")    
    def constructCommand(self,toolCommand,commandpostfix,toolLocation,configFilePath,configFileName,program,ptraceFilePath): 
        command="cd "+toolLocation+" && "+toolCommand+" -config "+configFilePath+configFileName+" -ptrace "+ptraceFilePath+program+"_"+configFileName.replace(".cfg","")+".trc"+" : "+program+" "+commandpostfix
        print(command)
        return command
    def constructCommandPipeView(self,toolCommand,toolLocation,configFilePath,configFileName,pipeviewPath): 
        command="cd "+toolLocation+" && "+toolCommand+" "+configFilePath+configFileName+" >> "+pipeviewPath+configFileName.replace(".trc","")+".txt"
        print(command)
        return command
class UpdateConfig:
    """A python program to update the cfg or config files attributes"""
    
    
    def __init__(self,seperator=''):
     
      self.seperator=seperator
    def configLinesList(self,filePath):
        linesList =[]
        with open(filePath,'r') as configFile:
          linesList = list(configFile)
        return linesList
    def updateConfigTypeNumber(self,linesList,configurations):
        updatedList =[]
        updationKeys = configurations.keys()
        print(updationKeys)
        for line in linesList:
            configKey = re.compile("\s+").split(line)[0].strip()
            # print("configkey",configKey)
               
            if(configKey in updationKeys ):
                # print("configkey",configKey)
            
                line = configKey+" "+configurations.get(configKey)+"\n"
                # print("line",line)
              
            updatedList.append(line)
            
        return updatedList
    def createNewConfigFile(self,updatedList,fileName):
       with open(fileName,'w') as updatedFile:
           for line in updatedList:
               updatedFile.write(line)
       print("Sucessfully Created the Updated Config")

def splitParameterValue(row):
    # print(row)
    parameterValue = row.str.split("#")[0]
    # print(parameterValue[0])
    parameterValue = parameterValue[0].split()
    parameter = parameterValue[0]
    value = parameterValue[1]
    # print(parameter)
    # print(value)
    return parameter,value

# input folder of the project contains a parameter configuration that defines the parameters to be changed 
configInputFilePath = "./SA1SE2/input/parameterconfig.txt"
configs=[]
##################################################################################
##                                                                              ##           
##    Below Variables need to updated to configure simulation on your system    ##
##                                                                              ##
##################################################################################
# path to the location where script is saved -Please change /home/sv/Desktop/ -> Your local location of Script Folder
scriptDirectoryPath = "/home/sairam/Desktop/SA1-InputFiles/"

#Simple scalar simulator installed location Please change /home/sv/Desktop/How-to-install-SimpleScalar-on-Ubuntu/ -> Your location of simple scalar simulator
simpleScalarDirectoryPath = "/home/sairam/Desktop/How-to-install-SimpleScalar-on-Ubuntu/"

##################################################################################
##                                                                              ##           
##    End of Variables That needs to be changed                                 ##
##                                                                              ##
##################################################################################



toolCommand=simpleScalarDirectoryPath+"build/simplesim-3.0/sim-outorder"
# Location of the example folder where executable files are present 
toolLocation=simpleScalarDirectoryPath+"example"

toolCommandPipeview =  simpleScalarDirectoryPath+"build/simplesim-3.0/pipeview.pl"
# the folder where the configuration files will be created
configFilePath= scriptDirectoryPath+"SA1SE2/config/"
# Resultant File path where the result of executing the config for different programs needs to be stored 
resultFilePath=scriptDirectoryPath+"SA1SE2/result/"
# Resultant File path where ptrace of the executed commands is stored 

ptraceFilePath=scriptDirectoryPath+"SA1SE2/ptrace/"
# Results of File path where pipeview of the ptrace commands is stored 
pipeviewFilePath = scriptDirectoryPath+"SA1SE2/pipeview/"
#
assemblyFilePath = scriptDirectoryPath+"SA1SE2/assembly/"


defaultConfigurationFile ="sa1se2-default.cfg"
commandPostFix=""
programs = ["fmath","main","llong"]

# the above parameters can be configured in input/parameterconfig as well

readConfig= ReadInputConfig()
configData =readConfig.getInputConfig(configInputFilePath) 
configs=configData['configs']



print(configs)
exeCommand = ExecuteCommand()
for config in configs:
    newConfigFileName=config['newconfigfilename']
    keys=config['keys']
    print(keys)
    configFileName=config['newconfigfilename']
    resultFileName=config['resultfilename']
    
    updateDefaultConfig = UpdateConfig("\t")
    linesList = updateDefaultConfig.configLinesList(configFilePath+defaultConfigurationFile)
    updatedList = updateDefaultConfig.updateConfigTypeNumber(linesList,keys)
    updateDefaultConfig.createNewConfigFile(updatedList,configFilePath+newConfigFileName)
    
    for program in programs:
        command = exeCommand.constructCommand(toolCommand,commandPostFix,toolLocation,configFilePath,configFileName,program,ptraceFilePath)
        output=exeCommand.getCommandOutput(command)
        exeCommand.saveCommandOutput(output,resultFilePath+program+"_"+resultFileName)
        exeCommand.executeCommand(command)
# The Sim out order results are stored in results folder
print("============== Completed Simulation for Out of Order All configs and Programs =========================")
# Extracting the parameter and values from the result file 
resultFilePath = "SA1SE2/result/"
resultFileNames = [f for f in listdir(resultFilePath) if isfile(join(resultFilePath, f))]
resultFileNames = sorted(resultFileNames)
outputFilePath = 'SA1SE2/simulationstats/'
print(resultFileNames)
for file in resultFileNames:
    print(file)
    df = pd.read_csv(resultFilePath+file,delimiter="/t",names=['parameter'])
    # print(df.columns)
   
    idx = df[df.iloc[:,0].str.contains('sim_num_insn')]
    idx = idx.index[0]
   
    simulationStat = pd.DataFrame()
    
    df = df[idx:]
    
    simulationStat[['parameter','value']] = df.apply(lambda row: splitParameterValue(row), axis=1, result_type='expand')
    file = file.replace('.txt','')
    simulationStat.to_csv(outputFilePath+file+'.csv',index=False)
print("============================ Completed Extracting Parameter and Value from Results   =============================")
print("============================ Creating the comparison result for all config files =================================")
configFilePath = "SA1SE2/simulationstats/"
configList = [f for f in listdir(configFilePath) if isfile(join(configFilePath, f))]
configList = sorted(configList)
compareFilesList = []

for config in configList:
    compareFilesList.append("SA1SE2/simulationstats/"+config)
compareFiles = []
for fileName in compareFilesList:
    print(fileName)
    compareFiles.append(pd.read_csv(fileName,index_col=False))

combined_df = pd.concat(compareFiles,axis='columns',keys=configList)
resultFileName = "sa1se2-result"
combined_df.to_csv('SA1SE2/comparison/'+resultFileName+'.csv')
print("========================== Completed Creating the comparison file ==================================")


ptraceFileList = [f for f in listdir(ptraceFilePath) if isfile(join(ptraceFilePath, f))]
print(ptraceFileList)
for ptrace in ptraceFileList:
    print(ptraceFileList)
    command = exeCommand.constructCommandPipeView(toolCommandPipeview,toolLocation,ptraceFilePath,ptrace,pipeviewFilePath)
    output=exeCommand.getCommandOutput(command)
    exeCommand.executeCommand(command)

print("========================== Completed Creating the ptrace files ==================================")


pipeviewFileList = [f for f in listdir(pipeviewFilePath) if isfile(join(pipeviewFilePath, f))]

for pipeview in pipeviewFileList:
    print("File Name", pipeview)
    file = open(pipeviewFilePath+pipeview,'r')
    lines = file.readlines()
    assemblyCode = []
    assemblyCode.append("No of lines")
    lineno = 0
    pipeviewlineno = 0
    pipeviewassemblymap = {}
    for line in lines:
        if line.__contains__("="):
            assemblyCode.append(str(lineno+1)+" : "+line)
            lineno+=1
            pipeviewassemblymap[lineno] = pipeviewlineno
        pipeviewlineno+=1
    assemblyCode[0] = "Total Instructions :"+str(lineno)+'\n'
    I = lineno
    X = (int)(lineno/3)
   
    Xend = X+100
    
    
    Y = 2*(int)(lineno/3)
    Yend = Y+100
    
    lineno = 0
    XCycleNo = ""
    XendCycleNo = ""
    temp = pipeviewassemblymap[X]
    while lines[temp].__contains__("@")== False:
        temp = temp-1
        
    XCycleNo = lines[temp]
    temp = pipeviewassemblymap[Xend]
    while lines[temp].__contains__("@")== False:
        temp = temp+1
        
    XendCycleNo = lines[temp]
    
    XlinesListAssembly = lines[pipeviewassemblymap[X]:temp]
    
    xpipeviewfile = open(pipeviewFilePath+"X_"+pipeview,'w')
    for line in XlinesListAssembly:
        xpipeviewfile.write(line)
    xpipeviewfile.close()
    traceFile = open(ptraceFilePath+pipeview.replace('txt','trc'),'r')
    traceLines = traceFile.readlines()
    XlinesTraceStart = 0 
    XlinesTraceEnd = 0
    traceLineNo = 0
    for line in traceLines:
        
        if line.strip().__contains__(XCycleNo.strip()):
            
            XlinesTraceStart = traceLineNo
        if line.strip().__contains__(XendCycleNo.strip()):
            
            XlinesTraceEnd = traceLineNo
        traceLineNo+=1
    XlinesListTrace = traceLines[XlinesTraceStart:XlinesTraceEnd]
    xtracefile = open(ptraceFilePath+"X_"+pipeview.replace('txt','trc'),'w')
    for line in XlinesListTrace:
        xtracefile.write(line)
    xtracefile.close()
       

    lineno = 0
    YCycleNo = ""
    YendCycleNo = ""
    temp = pipeviewassemblymap[Y]
    while lines[temp].__contains__("@")== False:
        temp = temp-1
        
    YCycleNo = lines[temp]
    temp = pipeviewassemblymap[Yend]
    while lines[temp].__contains__("@")== False:
        temp = temp+1
       
    YendCycleNo = lines[temp]
    
    YlinesListAssembly = lines[pipeviewassemblymap[Y]:temp]
    
    Ypipeviewfile = open(pipeviewFilePath+"Y_"+pipeview,'w')
    for line in YlinesListAssembly:
        Ypipeviewfile.write(line)
    Ypipeviewfile.close()
    traceFile = open(ptraceFilePath+pipeview.replace('txt','trc'),'r')
    traceLines = traceFile.readlines()
    YlinesTraceStart = 0 
    YlinesTraceEnd = 0
    traceLineNo = 0
    for line in traceLines:
        
        if line.strip().__contains__(YCycleNo.strip()):
            print("Line",line)
            YlinesTraceStart = traceLineNo
        if line.strip().__contains__(YendCycleNo.strip()):
            print("Line",line)
            YlinesTraceEnd = traceLineNo
        traceLineNo+=1
    YlinesListTrace = traceLines[YlinesTraceStart:YlinesTraceEnd]
    Ytracefile = open(ptraceFilePath+"Y_"+pipeview.replace('tYt','trc'),'w')
    for line in YlinesListTrace:
        Ytracefile.write(line)
    Ytracefile.close()
    

    assemblyFile = open(assemblyFilePath+pipeview,'w')
    assemblyFile.writelines(assemblyCode)
    XassemblyFile = open(assemblyFilePath+'X_'+pipeview,'w')
    XassemblyFile.writelines(assemblyCode[X:Xend+1])
    YassemblyFile = open(assemblyFilePath+'Y_'+pipeview,'w')
    YassemblyFile.writelines(assemblyCode[Y:Yend+1])
    assemblyFile.close()
    
    
print("========================== Completed Creating the Assembly files ==================================")
