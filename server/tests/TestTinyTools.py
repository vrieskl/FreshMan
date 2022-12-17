import unittest
from server.classes.TinyTools import ConfigSettings, Content


class TestTinyTools(unittest.TestCase):

    __JSON_TEXT: str = '''
        {"dsn": "mysql:host=localhost",
          "user-name": "test",
          "password_file_name" : "/tmp/pw.txt"
         }'''

    CONTENT = 'TheLazyFoxJumpedOverTheSquareBox'
    FILE_NAME = '../data/tmp.txt'

    def test_config_settings(self):
        config = ConfigSettings(self.__JSON_TEXT)
        self.assertEqual('test', config.get('user-name'))
        self.assertEqual('', config.get('no no no'))
        self.assertTrue(config.has('dsn'))
        self.assertFalse(config.has('no no no'))

    def test_content(self):
        Content.put(self.FILE_NAME, self.CONTENT)
        self.assertEqual(self.CONTENT, Content.get(self.FILE_NAME))


if __name__ == '__main__':
    unittest.main()
