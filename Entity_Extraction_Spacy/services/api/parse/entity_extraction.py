import warnings
warnings.filterwarnings("ignore")
import json
from services.api.jobs.tasks import get_msa_entities_async
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)


class EntityExtraction(object):

    def on_post(self, req, resp):
        doc = json.loads(req.stream.read().decode('latin1'))
        get_msa_entities_async.delay(doc)
        response = {"status": "MSA entities extraction in progress!"}
        logger.info("[{}] MSA API Acknowledgment sent".format(doc["callBack"]["fileName"]))
        resp.body = json.dumps(response)