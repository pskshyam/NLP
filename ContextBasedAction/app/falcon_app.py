import falcon
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware
from app.app_middleware.request_process import RequestBodyJSONProcessMiddleware
from app.app_middleware.response_process import ResponseJSONProcessMiddleware
from app.common.exceptionHandler import set_exception_handlers
from app.startup import add_routes, autoload


cors = CORS(allow_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True,
            max_age=720000)

dl_middlewares = [
    MultipartMiddleware(),
    ResponseJSONProcessMiddleware(),
    RequestBodyJSONProcessMiddleware(),
    cors.middleware
]


def create_application():
    app = falcon.API(middleware=dl_middlewares)
    autoload("app/rest/api")
    add_routes(app)
    set_exception_handlers(app)

    return app


print("Starting DL App")
app = create_application()


