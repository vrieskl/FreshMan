from abc import ABC, abstractmethod

from DataSetDef import DataSet
from typing import List, Dict, Tuple, Any
import mysql.connector as mc
import sqlite3

Parent = str
Child = str


class DataBase(ABC):
    """ Abstract class for database actions"""

    def __init__(self, place_holder: str = 's%'):
        self._connection = None
        self._place_holder = place_holder

    @abstractmethod
    def exec(self, statement: str, parameters: Tuple = ()):
        pass

    @abstractmethod
    def insert(self, table_name: str, parameters: Dict[str, Any]) -> int:
        pass

    def insert_data_set(self, table_name: str, data_set: DataSet) -> int:
        column_names = data_set.get_column_names()
        for row in data_set.get_data():
            self.insert(table_name, {column_names[i]: row[i] for i in range(0, len(column_names))})
        return data_set.size()

    def delete_data_set(self, table_name: str, key_field_name: str, data_set: DataSet) -> int:
        """ delete row(s) from table_name with where clause key_field_name """
        key_field_index = data_set.get_field_index(key_field_name)
        delete_count = 0
        for row in data_set.get_data():
            delete_count += self.delete(table_name, {key_field_name: row[key_field_index]})
        return delete_count

    def update_data_set(self, table_name: str, key_field_name: str, data_set: DataSet) -> int:
        """ delete row(s) from table_name with where clause key_field_name """
        update_count = 0
        for index in range(0, data_set.size()):
            value_pairs = data_set.get_row_dict(index)
            update_count += self.update(table_name, {key_field_name: value_pairs[key_field_name]}, value_pairs)
        return update_count

    @abstractmethod
    def select(self, select_statement: str, parameters: Tuple = ()) -> DataSet:
        pass

    # @abstractmethod
    # def delete(self, table_name: str, where_and: Dict[str, Any]) -> int:
    #     pass
    #
    # @abstractmethod
    # def update(self, table_name: str, where_and: Dict, value_pairs: Dict[str, Any]) -> int:
    #     pass

    def delete(self, table_name: str, where_and: Dict[str, Any]) -> int:
        """ Delete row(s) from table_name with where-and in Dict[field_name, value]"""
        cursor = self._connection.cursor()
        cursor.execute(
            'delete from ' + table_name +
            ' where ' + self.join_fields(' and ', tuple(where_and.keys())),
            tuple(where_and.values())
        )
        return cursor.rowcount

    def update(self, table_name: str, where_and: Dict[str, Any], value_pairs: Dict) -> int:
        """ Update rows in table_name with where-and in Dict[field_name, value] and value_pairs as updated fields"""
        cursor = self._connection.cursor()
        try:
            cursor.execute(
                'update ' + table_name +
                ' set ' + self.join_fields(', ', tuple(value_pairs.keys())) +
                ' where ' + self.join_fields(' and ', tuple(where_and.keys())),
                tuple(value_pairs.values()) + tuple(where_and.values())
            )
        except:
            raise Exception('Error update: ', table_name, value_pairs, where_and)
        finally:
            pass
        return cursor.rowcount

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def truncate(self, table_name: str):
        pass

    @abstractmethod
    def set_auto_increment(self, table_name: str, value=0):
        pass

    def insert_string(self, table_name: str, parameters: Tuple) -> str:
        # noinspection PyUnusedLocal
        tmp = 'insert into ' + table_name + '(' + ', '.join(parameters) + \
              ') values (' + ', '.join([self._place_holder for i in range(0, len(parameters))]) + ');'
        return tmp

    def join_fields(self, glue: str, field_names: tuple) -> str:
        """ Generate a string with 'field1 = %s glue field2 = %s' """
        return glue.join(field_name + ' = ' + self._place_holder for field_name in field_names)

    def select_one_field(self, select: str, parameters: Tuple[Any] = tuple()) -> Any:
        data_set: DataSet = self.select(select, parameters)
        if data_set.size() > 0:
            return data_set.get_field_value_by_index(0, 0)
        return None

    @staticmethod
    @abstractmethod
    def create_table_string(table_name: str, data_set: DataSet) -> str:
        pass

    # delivers List of child-parent tuples for the schema_name
    @abstractmethod
    def parent_child(self, schema_name: str) -> List[Tuple[Child, Parent]]:
        pass


class MySqlDb(DataBase):

    def parent_child(self, schema_name: str) -> List[Tuple[Child, Parent]]:
        sql = 'select T.TABLE_NAME child, coalesce(RC.REFERENCED_TABLE_NAME, \'\') parent' + \
              '  from information_schema.TABLES T' + \
              '  left join information_schema.REFERENTIAL_CONSTRAINTS RC' + \
              '    on T.TABLE_NAME = RC.TABLE_NAME' + \
              '   and T.TABLE_SCHEMA=RC.CONSTRAINT_SCHEMA' + \
              ' where T.TABLE_TYPE= \'BASE TABLE\'' + \
              '   and T.TABLE_SCHEMA = %s;'
        return self.select(sql, (schema_name,)).get_data()

    def __init__(self, user: str, password: str, host: str, database: str):
        super(MySqlDb, self).__init__('%s')
        self._connection = mc.connect(user=user, password=password, host=host, database=database)

    def exec(self, statement: str, parameters: Tuple = ()):
        self._connection.cursor().execute(statement, parameters)

    def insert(self, table_name: str, parameters: Dict[str, Any]) -> int:
        cursor = self._connection.cursor()
        try:
            cursor.execute(self.insert_string(table_name, tuple(parameters.keys())), tuple(parameters.values()))
        except:
            raise Exception('Error insert: ', table_name, parameters)
        finally:
            pass
        return cursor.lastrowid

    def select(self, select_statement: str, parameters: Tuple = ()) -> DataSet:
        cursor = self._connection.cursor()
        cursor.execute(select_statement, parameters)
        return DataSet(tuple(cursor.description[i][0] for i in range(0, len(cursor.description))), cursor.fetchall())

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

    def truncate(self, table_name: str):
        self.exec('truncate ' + table_name)

    def set_auto_increment(self, table_name: str, value: int = 0):
        self.exec('alter table ' + table_name + ' auto_increment = %s', (value,))

    @staticmethod
    def create_table_string(table_name: str, data_set: DataSet) -> str:
        varchar_clause = ' varchar(100) not null default \'\''
        join_string = varchar_clause + ", \n"
        return 'create or replace table ' + table_name + '(\nId int unsigned auto_increment  primary key,\n' + \
               join_string.join(data_set.get_column_names()) + varchar_clause + '\n) collate=utf8_unicode_ci;\n'


class SqLiteDb(DataBase):

    def parent_child(self, schema_name: str) -> List[Tuple[str, str]]:
        pass

    def __init__(self, database_name: str):
        super().__init__('?')
        self._connection = sqlite3.connect(database_name)

    def exec(self, statement: str, parameters: Tuple = ()):
        self._connection.cursor().execute(statement, parameters)

    def insert(self, table_name: str, parameters: Dict[str, Any]) -> int:
        cursor = self._connection.cursor()
        cursor.execute(self.insert_string(table_name, tuple(parameters.keys())), tuple(parameters.values()))
        return cursor.lastrowid

    def select(self, select_statement: str, parameters: Tuple = ()) -> DataSet:
        cursor = self._connection.cursor()
        cursor.execute(select_statement, parameters)
        return DataSet(tuple(cursor.description[i][0] for i in range(0, len(cursor.description))), cursor.fetchall())

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()

    def truncate(self, table_name: str):
        self.exec('delete from ' + table_name)

    def set_auto_increment(self, table_name: str, value=0):
        self.exec('update `sqlite_sequence` set `seq`=? where `name`=?', (value, table_name))

    @staticmethod
    def create_table_string(table_name: str, data_set: DataSet) -> str:
        pass

