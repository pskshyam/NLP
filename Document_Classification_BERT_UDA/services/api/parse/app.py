import falcon
from services.api.parse.document_classification import DocumentClassification
from falcon_multipart.middleware import MultipartMiddleware
from services.api.common.exception_handler import set_exception_handlers
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)

api = application = falcon.API(middleware=[MultipartMiddleware()])

doc_classifier = DocumentClassification()
api.add_route('/api/parse/predict_label', doc_classifier)
logger.info("#####################")
logger.info("Application is ready")
logger.info("#####################")
set_exception_handlers(api)
