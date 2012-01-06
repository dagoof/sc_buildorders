import functools, sc_units, operator, itertools
import decorators, func_utils

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

    @property
    def available_tech_tree(self):
        tech_tree = {}
        for unit, tech_path in zip(self.available_tech,
                map(operator.attrgetter('full_requirements'),
                    self.available_tech)):
            func_utils.dict_create_path(tech_path,
                    tech_tree).update({ unit : {} })
        return tech_tree

    def add_unit(self, unit):
        if unit.valid_with_respect_to(self.active_units,
                self.available_units):
            for more in unit.consumes_with_respect_to(self.active_units):
                self._units.remove(more)
            self._unit_order.append(unit)
            for more in sc_units.unit_wrapper(unit):
                self._units.append(more)
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
    
