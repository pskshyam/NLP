from flask import Flask
from flask import jsonify
from flask import request, json
import global_variables
from SentenceSemanticService import SentenceSemanticService
from modelSessionManager import SessionManager
from logger.logger import set_up_logging
logger = set_up_logging(__name__)

app = Flask(__name__)



@app.before_first_request
def before_request(): # reload model into modelSessionList before first request
    try:
        logger.info("In Before Request Reloading Model")
        global_variables.modelSessionList = {}
        global_variables.all_kbids = {}
    except Exception as e:
        logger.exception(str(e))


@app.route('/reload', methods=['GET', 'POST'])
def runReload(): # reload api for reloading model
    try:
        logger.info("In runReload Method reloading Model with reload api")
        kbid = json.loads(request.data)['kbid']
        logger.info("Request for Kd id :"+str(kbid))
        if SessionManager.getModelSessionByKbid(kbid):
            SessionManager.deleteModelSessionByKbid(kbid)
        SentenceSemanticService.define_placeholders()
        SentenceSemanticService.loadTrainedDataStoreSession(kbid)
        return jsonify({"status": "success", "message": "Model Reloaded Sucessfully"}), 200
    except Exception as e:
        logger.error("Issue While Reloading Model ! Please Try in Sometime"+str(e))
        return jsonify({"status": "failure", "message": "Issue While Reloading Model ! Please Try in Sometime"}), 500


@app.route('/predict', methods=['GET', 'POST'])
def runPrediction(): # prediction api
    try:
        logger.info("In Predict Method start")
        userQuery = json.loads(request.data)['question'].lower()
        kbid = json.loads(request.data)['kb_id']
        topN = json.loads(request.data)['top_n']
        logger.info("Question : "+str(userQuery))

        if not SessionManager.getModelSessionByKbid(kbid):
            SentenceSemanticService.define_placeholders()
        try:
            SentenceSemanticService.loadTrainedDataStoreSession(kbid)
            # userQuery = 'How many online surveys can I participate'
            matched_statement = SentenceSemanticService.process(userQuery=userQuery, kbid=kbid, topN=topN)
            logger.info("Matching Statement is :" + str(matched_statement))

            result = []
            for match_question, matched_score, question_id, answer in matched_statement:
                result.append(
                    {"matched_question_id": question_id, "matched_question": match_question, "score": str(matched_score),"answer": answer})
            return jsonify(result),200
        except Exception as e:
            return jsonify(
                {"status": "failure", "message": "Issue While Reloading Model ! Please Try in Sometime"}), 500
            logger.info("runPrediction: Error while reloading the model : " + str(e))

    except Exception as e:
        logger.info("Error : "+str(e))
        return jsonify({"message": "Service Not Found ! Please Try After Sometime", "status": "failed"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
