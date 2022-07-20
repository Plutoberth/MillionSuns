class Battery:
    def __init__(self, capacity_kwh: float, energy_kwh: float, charge_rate: float, efficiency: float):
        self._charge_rate = charge_rate
        self._efficiency = efficiency
        self._capacity = capacity_kwh
        assert energy_kwh <= capacity_kwh
        self._curr_energy = energy_kwh

    def get_max_charge(self):
        max_charge_at_efficiency = (self._capacity - self._curr_energy) / self._efficiency
        return min(
            max_charge_at_efficiency,
            self._capacity * self._charge_rate
        )

    def calc_allowed_charge(self, desired_kwh):
        return min(
            self.get_max_charge(),
            desired_kwh
        )

    def get_max_discharge(self):
        return min(
            self._curr_energy,
            self._capacity * self._charge_rate
        )

    def calc_allowed_discharge(self, desired_kwh):
        return min(
            desired_kwh,
            self.get_max_discharge()
        )

    def charge(self, kwh):
        assert kwh <= self.get_max_charge()
        self._curr_energy += kwh

    def discharge(self, kwh):
        assert kwh <= self.get_max_discharge()
        self._curr_energy -= kwh

    def get_energy_kwh(self):
        return self._curr_energy

    def get_capacity_kwh(self):
        return self._capacity
