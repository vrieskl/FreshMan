import csv
from server.classes.DataSetDef import DataSet
from server.classes.DataSetIoDef import DataSetIO


class DataSetCsv(DataSetIO):
    """ Read - Write a Dataset to-from Csv
    """

    def __init__(self, file_name: str, delimiter: str = ';', quote_char: str = '"'):
        self._delimiter = delimiter
        self._quote_char = quote_char
        self._file_name = file_name

    def write(self, data_set: DataSet):
        with open(self._file_name, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=self._delimiter, quotechar=self._quote_char,
                                quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            writer.writerow(list(data_set.get_column_names()))
            for row in data_set.get_data():
                writer.writerow(list(row))

    def read(self) -> DataSet:
        data_set = DataSet()
        first = True
        with open(self._file_name, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=self._delimiter, quotechar=self._quote_char)
            for row in csv_reader:
                if first:
                    data_set.set_column_names(tuple(row))
                    first = False
                else:
                    data_set.append_row(tuple(row))
        return data_set
