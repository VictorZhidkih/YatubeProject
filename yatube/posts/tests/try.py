import unittest


class TestExample(unittest.TestCase):
    """Демонстрирует принцип работы тестов"""
    @classmethod
    def setUpClass(cls):        
        print('setUpClass выполнен')

    @classmethod
    def tearDownClass(cls):
        print('tearDownClass выполнен')

    def setUp(self):
        print('setUp выполнен')

    def test_one(self): 
        print('Первый тест выполнен')

    def test_two(self): 
        print('Второй тест выполнен')


if __name__ == '__main__':
    unittest.main() 