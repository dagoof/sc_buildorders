import functools, sc_units

class BuildElement(object):
    def __init__(self, unit):
        pass


class BuildOrder(object):
    def __init__(self, *units):
        self._unit_order = []
        self._units = []
        self._tech = []
        for unit in units:
            self.add_unit(unit)

    @classmethod
    def based_on(cls, base):
        return cls(*base.active_units)

    @property
    def active_units(self):
        return self._units

    @property
    def available_tech(self):
        return self._tech

    def unit_valid(self, unit):
        for c in unit.consumes:
            if c not in self.active_units:
                return False
        for r in unit.requirements:
            if r not in self.active_units:
                return False
        return True

    def add_unit(self, unit):
        if self.unit_valid(unit):
            self._unit_order.append(unit)
            self._units.append(unit)
            for tech in unit.allows:
                if tech not in self.available_tech:
                    self._tech.append(tech)
            for consume in unit.consumes:
                self._units.remove(consume)
        else:
            raise Exception('%r requirements not met' % unit)
        return self

zerg_base = BuildOrder(*[sc_units.drone] * 6 + [sc_units.hatchery])
#protoss_base = BuildOrder(sc_units.nexus, *([sc_units.probe] * 6))

