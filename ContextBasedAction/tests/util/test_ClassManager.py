from util.ClassManager import Singleton


class SingletonTestClass(metaclass=Singleton):

    def __init__(self):
        pass


def test_create_multiple_classes():

    klass1 = SingletonTestClass()
    klass2 = SingletonTestClass()
    assert klass1 == klass2
