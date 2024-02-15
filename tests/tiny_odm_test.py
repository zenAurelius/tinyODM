import unittest

from tiny_odm.tinyodm import TinyModel

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

class Test(TinyModel):
        id_name = 'id'

class TestTinyODM(unittest.TestCase):

    def test_insert(self):
        """
        """
        db = TinyDB(storage=MemoryStorage)
        Test.collection = db.table('test')

        t = Test(id='1', name='toto')
        t.insert()

        self.assertTrue(t.exists())

    def test_get_id(self):
        db = TinyDB(storage=MemoryStorage)
        Test.collection = db.table('test')

        t0 = Test(id='0', name='child')
        t0.insert()
        t1 = Test(id='1', name='toto', child=t0)
        t1.insert()

        t2 = Test.get_id('1')

        self.assertTrue(isinstance(t2, Test))
        self.assertEqual(t2.id, '1')
        self.assertEqual(t2.name, 'toto')
        self.assertTrue(isinstance(t2.child, Test))
        self.assertEqual(t2.child.name, 'child')

    def test_get(self):
        db = TinyDB(storage=MemoryStorage)
        Test.collection = db.table('test')
        t0 = Test(id='1', name='toto')
        t0.insert()

        t1 = Test(id='1')
        t1.get()
        
        self.assertEqual(t1.name, 'toto')
        


if __name__ == '__main__':
    unittest.main()
