from typing import Dict
from server.classes.DataBase import DataBase


class Sensor:
    """" Get Database Id of a sensor Address
    """

    def __init__(self, data_base: DataBase):
        self.__cache: Dict[str, int] = {}
        self.__data_base = data_base

    def get(self, search: str) -> int:
        result = self.__cache.get(search)
        if result is not None:
            return result
        result = self.__data_base.select_one_field('select Id from Sensor where Address=%s', (search,))
        if result is not None:
            self.__cache[search] = result
            return result
        result = self.__data_base.insert('Sensor', {'Address': search})
        self.__cache[search] = result
        return result


class DeltaDetect:
    #   Detect if a value is more than the threshold
    def __init__(self, p_threshold=10):

        self.threshold = p_threshold
        self._samples = {}

    def set(self, key, value) -> bool:
        if key in self._samples:
            if abs(value - self._samples[key]) >= self.threshold:
                self._samples[key] = value
                return True
        else:
            self._samples[key] = value
            return True
        return False

    # make dictionary with changed values
    def check(self, data: Dict) -> Dict:
        return {key: data[key] for key in data.keys() if self.set(key, data[key])}


class Helpers:
    """ Some nice static methods
    """

    @staticmethod
    def split_message(in_string: str) -> Dict[str, float]:
        # input looks like:
        # 1179|284f8795f0013ce1:14.3125;28b34c95f0013cbc:14.5000;28e97895f0013cc6:14.4375;288e8395f0013c56:13.8750;
        result: Dict[str, float] = {}
        for item in in_string.split('|')[1][:-1].split(';'):
            tmp = item.split(':')
            result[tmp[0]] = float(tmp[1])
        return result
