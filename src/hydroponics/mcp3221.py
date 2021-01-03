import numpy
# -*- coding: utf-8 -*-


class mcp3221(object):
    def __init__(self, bus, index, address, adc_steps, v_ref, n_samples):
        self.bus = bus
        self.index = index
        self.adc_steps = adc_steps
        self.samples = numpy.empty(n_samples, dtype=float)
        self.sample_index = 0
        self.reset_samples()
        self.v_ref = v_ref
        self.address = address
        self.poly = None

    def set_calibration(self, x, y):
        poly = numpy.polyfit(x, y, 1)
        self.poly = poly

    def sample(self):
        data = self.bus.read_i2c_block_data(self.address, 0, 2)
        self.samples[self.sample_index] = data[0] << 8 | data[1]
        self.sample_index += 1
        if self.sample_index >= len(self.samples):
            self.sample_index = 0

    def reset_samples(self):
        self.sample_index = 0
        self.samples[:] = numpy.NaN

    def eval_samples(self):
        mean = numpy.nanmean(self.samples)
        voltage = self._adc_to_voltage(mean)
        physical_quantity = self._voltage_to_physical_quanitity(voltage)
        return voltage, physical_quantity

    def _adc_to_voltage(self, adc):
        return adc * self.v_ref / self.adc_steps

    def _voltage_to_physical_quanitity(self, voltage):
        return numpy.polyval(self.poly, voltage)
