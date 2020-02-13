import warnings
warnings.filterwarnings("ignore")
import json
from services.api.jobs.tasks import get_doc_links_async
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)


class DocLinking_process(object):

    def on_post(self, req, resp):
        doc = json.loads(req.stream.read().decode('latin1'))
        get_doc_links_async.delay(doc)
        response = {"status": "Document Linking in progress!"}
        logger.info("Document Linking Acknowledgment sent")
        resp.body = json.dumps(response)