import global_variables
from logger.logger import set_up_logging
logger = set_up_logging(__name__)


class SessionManager:

    """
    Description : Class For Managing All the session of all Models
    Author : Sachin Ichake

    """
    @classmethod
    def initialiseSession(self): # initialize session
        pass

    @classmethod
    def getModelSessionList(self): # returns model session from modelSessionList
        return global_variables.modelSessionList

    @classmethod
    def getModelSessionByKbid(self, kbid): #returns model session from modelSessionList based on kbid
        modelSessions = self.getModelSessionList()
        modelSession = modelSessions.get(kbid, {})
        return modelSession

    @classmethod
    def deleteModelSessionByKbid(self,kbid): #delete model session from modelSessionList based on kbid
         modelSession = self.getModelSessionList()
         try:
             del modelSession[kbid]
         except Exception as ex :
             logger.exception("Exception while deleting Model Session By KB id"+str(ex))


    @classmethod
    def setModelSessionByKbid(self, kbid, model_session=None):#add model session into modelSessionList
        try:
            modelSession = self.getModelSessionList()
            if kbid not in modelSession:
                modelSession[kbid] = {}

            modelSession[kbid] = model_session
            # return modelSession
        except Exception as ex:
            logger.exception("Exception while set Model Session By KB id",str(ex))
