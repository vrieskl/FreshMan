class TemperatureAverage:
    #   Calculate a running average of a temperature over specified number of samples

    def __init__(self, p_max_sample_count: int = 10):
        if p_max_sample_count <= 0:
            p_max_sample_count = 1
        self._max_sample_count = p_max_sample_count
        self._count: int = 0  # number of samples in the buffer
        self._current_sum: float = 0.0  # sum of all the values in the buffer
        self._samples = []  # buffer containing values
        self._index: int = -1  # Point to the most recent entry filled
        self._call_count: int = 0  # number of calls count
        self._max_call_count: int = p_max_sample_count * 100  # max_call_count before recalculating the sum
        # initialize the list
        self._samples = [0.0] * p_max_sample_count
        # old way
        # for index in range(0, p_max_sample_count):
        #     self._samples.append(0.0)

    #   add a value and get the average after processing this value
    def add_get(self, value: float) -> float:
        value = float(value)
        self._index = (self._max_sample_count + self._index + 1) % self._max_sample_count
        if self._count >= self._max_sample_count:
            self._current_sum -= self._samples[self._index]
        else:
            self._count += 1
        self._samples[self._index] = value
        self._call_count += 1
        if self._call_count > self._max_call_count:
            self._current_sum = self.calculate_sum(self._samples)
            self._call_count = 0
        else:
            self._current_sum += value
        return self._current_sum / self._count

    @staticmethod
    def calculate_sum(_samples) -> float:
        _sum = 0.0
        for value in _samples:
            _sum += value
        return _sum
