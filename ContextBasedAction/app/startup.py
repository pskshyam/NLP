import os
import pkgutil

class Route(object):
    """ Decorates RequestHandlers and builds a list of routes """

    _routes = []

    def __init__(self, uri):
        """ Initializes Route object
            Inputs:
                uri: uri of the Request Handler
        """
        self._uri = uri

    def __call__(self, _handler):
        """ Adds Handler instance and URI and append to the list of routes
            Input:
                _handler: falcon Request Handler object
        """
        self._routes.append([self._uri, _handler()])
        return _handler

    @classmethod
    def get_routes(cls):
        """ Returns list of routes """
        return cls._routes


def add_routes(app):
    """ Get all routes from handler decorator and add them to the app """
    routes = Route.get_routes()

    for r in routes:
        print("Registering %s" % (r))
        app.add_route(r[0], r[1])


def autoload(dirname):
    print(dirname)
    """ Autoload all modules in a directory """
    for path, directories, files in os.walk(dirname):
        for importer, package_name, _ in pkgutil.iter_modules([path]):
            # Supposedly, this means the module is already loaded, but that is
            # not the case for tests. It shouldn't hurt to reload them anyways.
            # if package_name not in sys.modules or True:
            print(package_name)
            importer.find_module(package_name).load_module(package_name)
