from random import randint
import pytest
from mimesis import Person

BASE_URL = "https://comp639prj2rar.pythonanywhere.com/"
APP_REGISTRATION_URL = "https://comp639prj2rar.pythonanywhere.com/register"

# BASE_URL = "http://127.0.0.1:5000/"
# APP_REGISTRATION_URL = "http://127.0.0.1:5000/register"


@pytest.fixture(scope="function")  # one instance reused across all tests
def fake_data():
    # Set a random seed to avoid repeated values
    seed = randint(1, 999999)
    return Person('en', seed=seed)
