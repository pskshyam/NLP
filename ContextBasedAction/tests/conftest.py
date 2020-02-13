import pytest
from util.ClassManager import Singleton


@pytest.fixture(autouse=True)
def reset_singletons():
    Singleton._instances = {}
