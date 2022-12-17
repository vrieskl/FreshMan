import json
from typing import Dict
from pathlib import Path

from server.classes.DataBase import MySqlDb


class ConfigSettings:
    def __init__(self, json_str: str):
        self.__parameters: Dict[str, str] = json.loads(json_str)

    def has(self, name: str) -> bool:
        return name in self.__parameters

    def get(self, name: str, default: str = ''):
        if name in self.__parameters:
            return self.__parameters[name]
        return default


class Content:
    @staticmethod
    def get(path: str) -> str:
        if Path(path).is_file():
            file = open(path, "r")
            data = str(file.read())
            file.close()
            return data

    @staticmethod
    def put(path: str, data: str):
        text_file = open(path, 'w')
        text_file.write(data)
        text_file.close()


class MySqlDbFactory:
    """ Factory to create MySqlDb from json string, file or settings
    """
    @staticmethod
    def settings(settings: ConfigSettings) -> MySqlDb:
        return MySqlDb(
            settings.get('user_name'),
            Content.get(settings.get('password_file_name')),
            settings.get('host'),
            settings.get('database')
        )

    @staticmethod
    def string(json_str: str) -> MySqlDb:
        return MySqlDbFactory.settings(ConfigSettings(json_str))

    @staticmethod
    def file(path: str) -> MySqlDb:
        return MySqlDbFactory.string(Content.get(path))
