from abc import ABC, abstractmethod
from DataSetDef import DataSet


class DataSetIO(ABC):
    """ Read - Write a Dataset Abstract class
    """

    @staticmethod
    @abstractmethod
    def write(data_set: DataSet):
        pass

    @staticmethod
    @abstractmethod
    def read() -> DataSet:
        pass
