import falcon
from falcon_cors import CORS
from services.api.parse.entity_extraction import EntityExtraction
from falcon_multipart.middleware import MultipartMiddleware
from services.api.common.exception_handler import set_exception_handlers
from services.api.parse.docLinking_process import DocLinking_process
from services.api.common.logger import set_up_logging
logger = set_up_logging(__name__)
import warnings
warnings.filterwarnings("ignore")

cors = CORS(allow_all_origins=True,
allow_all_headers=True,
allow_all_methods=True,
max_age=720000)

dl_middlewares = [
MultipartMiddleware(),
cors.middleware
]

api = application = falcon.API(middleware=dl_middlewares)

#doc linking
doc_link = DocLinking_process()
api.add_route('/doclinking', doc_link)

entity_extractor = EntityExtraction()
api.add_route('/msa_entities', entity_extractor)
logger.info("#####################")
logger.info("Application is ready")
logger.info("#####################")
set_exception_handlers(api)
