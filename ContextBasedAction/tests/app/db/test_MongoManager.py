import mongomock
from app.db.MongoManager import MongoConnection


def test_get_db(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    mocker.patch.object(mongo_client, 'get_database', return_value=True)
    mocker.patch.object(conn, 'raise_exception')
    conn.client = mongo_client
    conn.get_db(db_name)
    conn.client.get_database.assert_called_with(db_name)
    assert conn.client.get_database.call_count == 2
    conn.raise_exception.assert_not_called()


def test_get_db_false(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.client = mongo_client
    message = 'Database test_db does not exist. Please check your configuration file parameters and try again.'

    mocker.patch.object(mongo_client, 'get_database', return_value=False)
    mocker.patch.object(conn, 'raise_exception')

    conn.get_db(db_name)

    conn.client.get_database.assert_called_once_with(db_name)
    conn.raise_exception.assert_called_once_with(message)


def test_get_collection_exists(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.db = mongo_client.db

    mocker.patch.object(mongo_client.db, 'get_collection', return_value=True)
    mocker.patch.object(conn.db, 'create_collection')
    mocker.patch.object(conn, 'raise_exception')

    conn.get_collection(coll_name)

    conn.db.get_collection.assert_called_with(coll_name)
    assert conn.db.get_collection.call_count == 2
    conn.db.create_collection.assert_not_called()
    conn.raise_exception.assert_not_called()


def test_get_collection_creating(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.db = mongo_client.db
    conn.mongo_db_model_info_collection = coll_name

    mocker.patch.object(mongo_client.db, 'get_collection', return_value=False)
    mocker.patch.object(conn.db, 'create_collection')
    mocker.patch.object(conn, 'raise_exception')

    conn.get_collection(coll_name)

    conn.db.get_collection.assert_called_with(coll_name)
    assert conn.db.get_collection.call_count == 2
    conn.db.create_collection.assert_called_once_with(coll_name)
    conn.raise_exception.assert_not_called()


def test_find_document_by_id(mocker):
        db_name = "test_db"
        coll_name = "test_coll"
        query = {'query', 'query_value'}

        mongo_client = mongomock.MongoClient()
        conn = MongoConnection(db_name, coll_name)
        conn.collection = mongo_client.collection

        mocker.patch.object(conn.collection, 'find_one', return_value=False)

        conn.find_document_by_id(query)

        conn.collection.find_one.assert_called_once_with(query)


def test_get_collection_except(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    message = 'Collection does not exist in test_db database.' \
              'Please check your configuration file parameters and try again.'
    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.db = mongo_client.db
    conn.mongo_db_model_info_collection = "different_collection"

    mocker.patch.object(mongo_client.db, 'get_collection', return_value=False)
    mocker.patch.object(conn.db, 'create_collection')
    mocker.patch.object(conn, 'raise_exception')

    conn.get_collection(coll_name)

    conn.db.get_collection.assert_called_once_with(coll_name)
    conn.db.create_collection.assert_not_called()
    conn.raise_exception.assert_called_once_with(message)


def test_update_document(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    query = {'query': 'query_value'}
    document = {'document', 'document_value'}

    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.collection = mongo_client.collection

    mocker.patch.object(conn.collection, 'update', return_value=False)

    conn.update_document(query, document)

    conn.collection.update.assert_called_once_with(query, document)

def test_create_document(mocker):

    db_name = "test_db"
    coll_name = "test_coll"
    document = {'document', 'document_value'}

    mongo_client = mongomock.MongoClient()
    conn = MongoConnection(db_name, coll_name)
    conn.collection = mongo_client.collection

    mocker.patch.object(conn.collection, 'insert_one', return_value=False)

    conn.create_document(document)

    conn.collection.insert_one.assert_called_once_with(document)