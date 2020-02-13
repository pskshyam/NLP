import uuid
from uuid import UUID
from util.id_generator import new_id


def test_new_id(mocker):
    mocker.patch.object(uuid, 'uuid4', return_value=UUID('{12345678-1234-5678-1234-567812345678}'))
    res = new_id()
    assert res == '12345678123456781234567812345678'
