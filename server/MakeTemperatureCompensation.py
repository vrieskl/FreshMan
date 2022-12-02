from DataBase import MySqlDb, DataBase

sql_statement = \
    '''
        select S.Address, AvgTemperature0, avg(AvgTemperature) avgAllTemperature, avg(M.Temperature) AvgSensorTemperature
            from Sensor S
            join Measure M on S.Id = M.SensorId
            join(
                    select M.SampleId, avg(M.Temperature) AvgTemperature, round(avg(M.Temperature), 0) AvgTemperature0
                    from Sensor S
                    join Measure M on S.Id = M.SensorId
                    where Reference in ('I', 'II', 'III', 'IIII')
                    group by 1
                    having count(*) = 4
                ) aa on aa.SampleId=M.SampleId
            where Reference in ('I', 'II', 'III', 'IIII')
            group by 1, 2
            order by 2,1
'''
db: DataBase = MySqlDb('adm', '1qazJI90!', 'pi0-2w', 'pico_data')
result = db.select(sql_statement)
# Example dict:
#                 key    avg  sen    avg  sen
# compensation = {'a': [4:0.13, 5: -0.15], }
compensation = {}
for record in result.get_data():
    data = {}
    address, all_avg, sensor = record[0], record[2], record[3]
    # print(address, all_avg, sensor, all_avg - sensor)
    if address in compensation:
        data = compensation[address]
    else:
        compensation[address] = data
    temp = int(round(sensor, 0))
    if temp in data:
        print('dubbel!', temp, address)
    data[temp] = all_avg - sensor
# make string for Python
for address in compensation.keys():
    data_str = ''
    start = 0
    end = 30
    for index in range(start, end):
        data = compensation[address]
        keys = sorted(data)
        value = 0.0
        if index in keys:
            value = data[index]
        else:
            if index < keys[0]:
                value = data[keys[0]]
            elif index > keys[len(keys)-1]:
                value = data[keys[len(keys)]]
            else:
                for runner in range(start, end - 1):
                    if index < keys[runner]:
                        value = (data[keys[runner]] + data[keys[runner-1]]) / 2
                        # print(keys)
                        # print(address, index, keys[runner], value, data[keys[runner]] , data[keys[runner+1]])
                        break
        data_str += str(index) + ':' + str(round(value, 2)) + ','
    print('\'' + address + '\':{' + data_str, '},')

# example output
compensation_example = {
    'a34':{1:.234, 2: 0.456, },
    'b67':{1:.234, 2: .456, },

}
