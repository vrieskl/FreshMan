from typing import List, Tuple, Dict, Any


class DataSet:
    """ Primary store of datasets
    """

    def __init__(self, column_names: Tuple = (), data=None):
        self._column_keys: Dict = {column_names[i]: i for i in range(0, len(column_names))}
        self._column_names = column_names
        if data is None:
            data = []
        self._data: List[Tuple] = data

    def get_column_names(self) -> Tuple:
        return self._column_names

    def set_column_names(self, column_names: Tuple):
        self._column_names = column_names

    def set_data(self, data: List[Tuple]):
        self._data = data

    def get_data(self) -> List[Tuple]:
        return self._data

    def get_row(self, index: int) -> Tuple:
        return self._data[index]

    def get_row_dict(self, index: int) -> Dict[str, Any]:
        row = self._data[index]
        return {self._column_names[col_index]: row[col_index] for col_index in range(0, len(self._column_names))}

    def get_field_index(self, column_name: str) -> int:
        return self._column_keys[column_name]

    def get_field_value_by_index(self, row_index: int, field_index: int):
        return self._data[row_index][field_index]

    def get_field_value_by_name(self, row_index: int, column_name: str):
        return self._data[row_index][self._column_keys[column_name]]

    def delete_row(self, row_index: int):
        self._data.pop(row_index)

    def append_row(self, row: Tuple):
        self._data.append(row)

    def update_row(self, row_index: int, row: Tuple):
        self._data[row_index] = row

    def size(self) -> int:
        return len(self._data)

    def get_column_list(self, column_index: int) -> List:
        """ List of values in the column specified by column_index """
        return [self._data[i][column_index] for i in range(0, len(self._data))]

    def get_list_index(self, key_column_index: int) -> Dict:
        """ Dictionary with key the values specified by the key_column_index,
            the value is the index in the list.
        """
        temp_dict: Dict = {}
        for index in range(0, self.size()):
            temp_dict[self.get_field_value_by_index(index, key_column_index)] = index
        return temp_dict

    def get_dict(self, key_column_name: str, value_column_name: str) -> Dict:
        """ Dictionary with key the values specified by the key_column_name,
            the value specified by value_column_name
        """
        key_index = self.get_field_index(key_column_name)
        value_index = self.get_field_index(value_column_name)
        return {self._data[i][key_index]: self._data[i][value_index] for i in range(0, len(self._data))}

