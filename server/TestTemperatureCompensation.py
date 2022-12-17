from pico.Temperature import Temperature
from server.classes.DataSetCsvDef import DataSetCsv

reader = DataSetCsv('data/samples2.csv', ',', '\'')
dataset = reader.read()
compensator = Temperature()
for record in dataset.get_data():
    temp1, address, temp, count = float(record[0]), record[1], float(record[2]), int(record[3])
    temp_corr = compensator.get(address, temp)
    print(address, 'avg all:', temp1, ', measured:', temp, 'corrected:', temp_corr, ', sample size:', count)
