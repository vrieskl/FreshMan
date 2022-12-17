# calculate compensations based on csv
# only first and
# csv:
# AvgTemperature1,Address,Temperature,count(*)
# 3.9, 284f8795f0013ce1, 4,     12
# 3.9, 288e8395f0013c56, 3.5,    9
# 3.9, 288e8395f0013c56, 3.5625, 3
# 3.9, 28b34c95f0013cbc, 4.375,  3
# 3.9, 28b34c95f0013cbc, 4.4375 ,9

from typing import Dict, List
from server.classes.DataSetCsvDef import DataSetCsv


class TempCount:

    def __init__(self, p_temp: float = 0.0, p_count: int = 0):
        self._temp_sum = 0.0
        self._count_sum = 0
        self.add(p_temp, p_count)

    def add(self, p_temp: float, p_count: int):
        self._temp_sum += p_temp * p_count
        self._count_sum += p_count

    def avg(self) -> float:
        return self._temp_sum / self._count_sum


class Compensation:

    def __init__(self):
        self._compensation: Dict[str: Dict[int: float]] = {'': {0: 0.0}}
        del self._compensation['']

    def add(self, p_address: str, p_temp: int, delta: float):
        if p_address in self._compensation:
            self._compensation[p_address][p_temp] = delta
        else:
            self._compensation[p_address] = {p_temp: delta}

    def dump(self, start: int, end: int) -> str:
        # dump as a python dictionary
        result: str = ''
        for key in self._compensation.keys():
            result += '\'' + key + '\': {'
            keys: List[int] = sorted(self._compensation[key].keys())
            for ndx in range(start, end):
                value: float = 0.0
                if ndx < keys[0]:
                    value = self._compensation[key][keys[0]]
                elif ndx > keys[len(keys) - 1]:
                    value = self._compensation[key][keys[len(keys)]]
                elif ndx in keys:
                    value = self._compensation[key][ndx]
                else:
                    for ndx2 in range(1, len(keys)):
                        if keys[ndx2] > ndx:
                            value = round(
                                (self._compensation[key][keys[ndx2 - 1]] + self._compensation[key][keys[ndx2]]) / 2,
                                3)
                            break
                result += str(ndx) + ': ' + str(value) + ', '
            result += '},' + "\r\n"
        return result


def calc_str(p_calc: Dict[str, TempCount]) -> str:
    result: str = ''
    for key in p_calc.keys():
        result += key + ': ' + str(round(p_calc[key].avg(), 2)) + ', '
    return result


reader = DataSetCsv('data/samples2.csv', ',', '\'')
dataset = reader.read()
NO_VALUE: float = -999.9
temperature1_key: float = NO_VALUE
compensation = Compensation()
calc: Dict[str, TempCount] = {'': TempCount()}
for record in dataset.get_data():
    temp1, address, temp, count = float(record[0]), record[1], float(record[2]), int(record[3])
    if temperature1_key != temp1:
        if temperature1_key != NO_VALUE:
            del calc['']
            print(str(temperature1_key), calc_str(calc))
            for addr in calc.keys():
                compensation.add(addr, int(round(calc[addr].avg(), 0)), round(calc[addr].avg() - temperature1_key, 3))
        calc = {'': TempCount()}
        temperature1_key = temp1
    if address in calc:
        calc[address].add(temp, count)
    else:
        calc[address] = TempCount(temp, count)
print(compensation.dump(0, 30))
# example output
compensation_example = {
    'a34': {1: .234, 2: 0.456, },
    'b67': {1: .234, 2: .456, },

}
