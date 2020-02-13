import falcon
from app.common.logger import set_up_logging

import traceback

logger = set_up_logging(__name__)


class ErrorHandler(object):
    @staticmethod
    def http(ex, req, resp, params):
        raise ex

    @staticmethod
    def unexpected(ex, req, resp, params):
        try:
            trace = traceback.format_exc()
            logger.exception('Application failed with an unknown error. This log is from app.common.exceptionHandler')
            # logger.exception(trace)
            # print 'trace = ', trace
            raise falcon.HTTPInternalServerError(
                "Application failed with an unknown error",
                trace
            )
        except Exception:
            logger.exception("######################## Unknown exception. Exception handler also failed #######################")
            raise falcon.HTTPInternalServerError(
                "Application failed with an unknown error",
                ""
            )


def set_exception_handlers(app):
    app.add_error_handler(Exception, ErrorHandler.unexpected)
    app.add_error_handler(falcon.HTTPError, ErrorHandler.http)
    app.add_error_handler(falcon.HTTPStatus, ErrorHandler.http)
