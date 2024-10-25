"""
"""
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage, MemoryStorage
from copy import deepcopy
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateSerializer, DateTimeSerializer
from tinydb_serialization import Serializer


def _enumerates(elements):
    """
    Enumerates a list or dict of elements

    if the element is a dict: return the items (key, value).
    if the element is a list: return an iterator over (index, item)
    """

    if isinstance(elements, dict):
        return elements.items()
    else:
        return enumerate(elements)


def _reads(elements):
    """
    Reads a list or dict of elements

    if element is a string for a FK: load the foreign object in place in the original list or dict.
    if element is a list or a dict: recursively call reads
    """

    for key, value in _enumerates(elements):
        if isinstance(value, str) and '|' in value:
            datas = value.split('|')
            print(datas)
            if datas[0] in TinyModel.models:
                elements[key] = TinyModel.models[datas[0]].get_id(datas[1])
        elif isinstance(value, (dict, list)):
            _reads(value)


def _writes(elements):
    """
    Writes a list or dict of elements

    - if element is a TinyModel: check if exist in db or insert it
      and replace it with the FK string (<class name>|id)
    - if element is a list or dict: recursively call writes
    """

    for key, value in _enumerates(elements):
        if isinstance(value, TinyModel):
            if value.exists() or value.insert():
                elements[key] = f"{value.__class__.__name__}|{value._id()}"
        elif isinstance(value, (dict, list)):
            _writes(value)

class TinyConnection:

    def __init__(self, dbfile=None, storage=None):
        stor = SerializationMiddleware(JSONStorage) if storage is None else storage
        file = dbfile if dbfile is not None else 'db.json'
        if stor != MemoryStorage:
            stor.register_serializer(DateTimeSerializer(), 'Datetime')
            stor.register_serializer(DateSerializer(), 'Date')
            #stor.register_serializer(TinyModelSerializer(), 'TinyModel')
            self.db = TinyDB(file, storage=stor)
        else:
            self.db = TinyDB(storage=stor)
        

    def register(self, clsModel, tableName):
        clsModel.collection = self.db.table(tableName)

class TinyModel:
    """Base Class for any model"""

    collection = None
    query = Query()
    id_name = None
    models = {}

    def __init__(self, **kwargs):
        setattr(self, self.__class__.id_name, None)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __init_subclass__(cls) -> None:
        """
        Initialization of subclasses

        Register any subclasses in models by name
        """

        TinyModel.models[cls.__name__] = cls

    @classmethod
    def instanciate(cls, doc):
        _reads(doc)
        n = cls(**doc)
        setattr(n, cls.id_name, doc.doc_id)
        return n

    @classmethod
    def get_id(cls, id: str):
        """
        Get a instance of the Model object from the DB by ID

        get the document from the collection and :
            - if doc exist reads it for FK and instanciate the object with it
            - else return None
        """

        doc = cls.collection.get(doc_id=id)
        if doc:
            return cls.instanciate(doc)
        else:
            return None

    @classmethod
    def get_all(cls):
        docs = cls.collection.all()
        for i, d in enumerate(docs):
            docs[i] = cls.instanciate(d)
        return docs

    @classmethod
    def remove_id(cls, id: str) -> None:
        """
        Remove a document from the DB

        Remove the document(s) where the id == parameter
        """

        cls.collection.remove(cls.query[cls.id_name] == id)

    @classmethod
    def exists_id(cls, id: str) -> bool:
        """
        Indicates if document fo id 'id' exists in collection of 'cls'
        """

        return id != None and cls.collection.contains(doc_id=id)
    
    @classmethod
    def search(cls, querie):
        docs = cls.collection.search(querie)
        print(docs)
        for i, d in enumerate(docs):
            docs[i] = cls.instanciate(d)
        print(docs)
        return docs

    def _id(self) -> str:
        """
        Return id, ie the attribute named by 'id_name'
        """

        return getattr(self, self.__class__.id_name)

    def remove(self):
        """
        Remove the document in the collection
        """

        self.remove_id(self._id())

    def get(self):
        """
        Get the object from DB with same id
        """

        tm = self.__class__.get_id(self._id())
        if tm:
            self.__dict__ = tm.__dict__
        else:
            self = None

    def exists(self):
        """
        Check existence of a document with id
        """
        return self.__class__.exists_id(self._id())

    def insert(self):
        """
        Insert a objet in his collection

        If object already exist in DB, do nothing
        for children, if doesn't exist in DB insert, replace them by the FK tag (cf. _writes)
        """
        if self.exists():
            return
        data = deepcopy(self.__dict__)
        del data[self.__class__.id_name]
        _writes(data)
        setattr(self, self.__class__.id_name, self.__class__.collection.insert(data))
        return self

    def update(self, fields=None):
        upd = {}
        if fields:
            upd = {f: self.__dict__[f] for f in fields}
        print(upd)
        self.__class__.collection.update(upd, doc_ids=[self._id()])

class TinyModelSerializer(Serializer):
    OBJ_CLASS = TinyModel  # The class this serializer handles

    def encode(self, obj):
        
        return data

    def decode(self, s):
        return datetime.fromisoformat(s)