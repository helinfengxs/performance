global runStatus
runStatus =1
global pingStaus
pingStaus =1
class EditGlobalParmas:
    def getRunStatus(self):
        global runStatus
        return runStatus
    def setRunStatus(self,status):
        global runStatus
        runStatus = status
    def getPingStaus(self):
        global pingStaus
        return pingStaus
    def setpingStaus(self,status):
        global pingStaus
        pingStaus = status