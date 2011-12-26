import functools, sc_units, operator, itertools
import decorators

class BuildElement(object):
    def __init__(self, unit):
        pass

class BuildOrder(object):
    def __init__(self, race_units, *units):
        self._race_units = race_units
        self._unit_order = []
        self._units = []
        for unit in units:
            self.add_unit(unit)

    @classmethod
    def based_on(cls, base):
        return cls(base._race_units, *base._unit_order)

    @property
    def active_units(self):
        return self._units

    @property
    @decorators.apply_f(list)
    def available_units(self):
        return itertools.chain.from_iterable(
                unit.acts_as for unit in self.active_units)

    @property
    def available_tech(self):
        return filter(operator.methodcaller('valid_with_respect_to',
            self.active_units,
            self.available_units), self._race_units)

    def unit_valid(self, unit):
        for c in unit.consumes:
            if c not in self.active_units:
                return False
        for r in unit.requirements:
            if r not in self.available_units:
                return False
        return True

    def add_unit(self, unit):
        if unit.valid_with_respect_to(self.active_units,
                self.available_units):
            self._unit_order.append(unit)
            self._units.append(unit)
            for consume in unit.consumes:
                self._units.remove(consume)
        else:
            raise Exception('%r requirements not met' % unit)
        return self

ZERG = functools.partial(BuildOrder, sc_units.zerg_units)
PROTOSS = functools.partial(BuildOrder, sc_units.protoss_units)
TERRAN = functools.partial(BuildOrder, sc_units.terran_units)

zerg_base = ZERG(*[sc_units.drone] * 7 + [sc_units.hatchery])
protoss_base = PROTOSS(sc_units.nexus, *([sc_units.probe] * 6))
terran_base = TERRAN(sc_units.command_center, *([sc_units.scv] * 7))

race_orders = {
    sc_units.Races.ZERG: ZERG,
    sc_units.Races.TERRAN: TERRAN,
    sc_units.Races.PROTOSS: PROTOSS,
}

race_builds = {
    sc_units.Races.ZERG: zerg_base,
    sc_units.Races.TERRAN: terran_base,
    sc_units.Races.PROTOSS: protoss_base,
}
    
