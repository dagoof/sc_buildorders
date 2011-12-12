import functools, operator, itertools

def apply_f(applied_f):
    def decorator(f):
        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            return applied_f(f(*args, **kwargs))
        return _wrapped
    return decorator

def reverse_args(f):
    @functools.wraps(f)
    def _wrapped(*args):
        return f(*reversed(args))
    return _wrapped

all_gameunits = {}

def register_gameunit(unit):
    all_gameunits[str(unit)] = unit

class GameResource(object):
    @classmethod
    def combine_resources(cls, *resources):
        return cls(sum(r.amount for r in resources if isinstance(r, cls)))
        #return cls(sum(map(operator.attrgetter('amount'),
            #filter(functools.partial(
                #reverse_args(isinstance), cls),
                #resources))))

    def __init__(self, amount):
        self.amount = amount

    def __repr__(self):
        return '<{_class}: {amount}>'.format(amount = self.amount,
                _class = self.__class__.__name__)

class Mineral(GameResource):
    pass

class Gas(GameResource):
    pass

game_resources = [Mineral, Gas]

class GameUnit(object):
    def __init__(self, name, reqs = (), costs = (), consumes = ()):
        self.name = name
        self._reqs = reqs
        self._costs = costs
        self._consumes = consumes
        self._deps = []
        register_gameunit(self)
        for req in self._reqs:
            req.register_dependent(self)

    def register_dependent(self, other):
        if other not in self._deps:
            self._deps.append(other)

    @property
    def requirements(self):
        return self._reqs

    @property
    @apply_f(list)
    def full_requirements(self):
        sofar = []
        for req in self._reqs:
            for more in req.full_requirements:
                if more not in sofar:
                    sofar.append(more)
                    yield more
            if req not in sofar:
                sofar.append(req)
                yield req

    @property
    def costs(self):
        return self._costs

    @property
    @apply_f(list)
    def full_costs(self):
        _costs = reduce(operator.add,
                [req.costs for req in self.full_requirements])
        _costs += self.costs
        for resource in game_resources:
            combined = resource.combine_resources(*_costs)
            if combined.amount:
                yield combined

    @property
    def consumes(self):
        return self._consumes

    @property
    @apply_f(list)
    def full_consumes(self):
        _consumes = reduce(operator.add,
                [req.consumes for req in self.full_requirements])
        _consumes += self.consumes
        for c in _consumes:
            yield c

    @property
    def allows(self):
        return self._deps

    @property
    def data_obj(self):
        return {
            'unit_name': self.name,
            'requires': self.full_requirements,
            'allows': self.allows,
        }

    def __repr__(self):
        return '<{_class}: {_name}>'.format(_name = self.name,
                _class = self.__class__.__name__)

    def __str__(self):
        return self.name

class UnitNames:
    hatchery = 'Hatchery'
    drone = 'Drone'
    spawning_pool = 'Spawning Pool'
    zergling = 'Zergling'
    baneling_nest = 'Baneling Nest'
    baneling = 'Baneling'
    roach_warren = 'Roach Warren'
    roach = 'Roach'
    lair = 'Lair'
    infestation_pit = 'Infestation Pit'
    infestor = 'Infestor'
    spire = 'Spire'
    mutalisk = 'Mutalisk'
    corrupter = 'Corrupter'
    hydralisk_den = 'Hydralisk Den'
    hydralisk = 'Hydralisk'
    hive = 'Hive'
    ultralisk_den = 'Ultralisk Den'
    ultralisk = 'Ultralisk'
    greater_spire = 'Greater Spire'
    brood_lord = 'Brood Lord'

    nexus = 'Nexus'
    pylon = 'Pylon'
    assimilator = 'Assimilator'
    probe = 'Probe'
    mothership = 'Mothership'
    gateway = 'Gateway'
    zealot = 'Zealot'
    sentry = 'Sentry'
    high_templar = 'High Templar'
    dark_templar = 'Dark Templar'
    stalker = 'Stalker'
    cybernetics_core = 'Cybernetics Core'
    forge = 'Forge'
    cannon = 'Cannon'
    warp_gate = 'Warp Gate'
    stargate = 'Stargate'
    twilight_council = 'Twilight Council'
    phoenix = 'Phoenix'
    void_ray = 'Void Ray'
    carrier = 'Carrier'
    robotics_facility = 'Robotics Facility'
    robotics_bay = 'Robotics Bay'
    immortal = 'Immortal'
    colossus = 'Colossus'
    observer = 'Observer'
    warp_prism = 'Warp Prism'
    templar_archives = 'Templar Archives'
    dark_shrine = 'Dark Shrine'
    fleet_beacon = 'Fleet Beacon'

"""
Zerg structures
"""

drone = GameUnit(UnitNames.drone,
        costs = [Mineral(50)])
hatchery = GameUnit(UnitNames.hatchery,
        costs = [Mineral(300)],
        consumes = [drone])
spawning_pool = GameUnit(UnitNames.spawning_pool,
        costs = [Mineral(200)],
        consumes = [drone])
baneling_nest = GameUnit(UnitNames.baneling_nest, [spawning_pool],
        costs = [Mineral(100), Gas(50)],
        consumes = [drone])
roach_warren = GameUnit(UnitNames.roach_warren, [spawning_pool],
        costs = [Mineral(150)],
        consumes = [drone])
lair = GameUnit(UnitNames.lair, [spawning_pool],
        costs = [Mineral(150), Gas(100)],
        consumes = [hatchery])
infestation_pit = GameUnit(UnitNames.infestation_pit, [lair],
        costs = [Mineral(100), Gas(100)],
        consumes = [drone])
spire = GameUnit(UnitNames.spire, [lair],
        costs = [Mineral(200), Gas(200)],
        consumes = [drone])
hydralisk_den = GameUnit(UnitNames.hydralisk_den, [lair],
        costs = [Mineral(100), Gas(100)],
        consumes = [drone])
hive = GameUnit(UnitNames.hive, [infestation_pit],
        costs = [Mineral(200), Gas(150)],
        consumes = [lair])
ultralisk_den = GameUnit(UnitNames.ultralisk_den, [hive],
        costs = [Mineral(150), Gas(200)],
        consumes = [drone])
greater_spire = GameUnit(UnitNames.greater_spire, [hive],
        costs = [Mineral(100), Gas(150)],
        consumes = [spire])


"""
Zerg units
"""

zergling = GameUnit(UnitNames.zergling, [spawning_pool],
        costs = [Mineral(25)])
ultralisk = GameUnit(UnitNames.ultralisk, [ultralisk_den],
        costs = [Mineral(300), Gas(200)])
hydralisk = GameUnit(UnitNames.hydralisk, [hydralisk_den],
        costs = [Mineral(100), Gas(50)])
corrupter = GameUnit(UnitNames.corrupter, [spire],
        costs = [Mineral(150), Gas(100)])
mutalisk = GameUnit(UnitNames.mutalisk, [spire],
        costs = [Mineral(100), Gas(100)])
infestor = GameUnit(UnitNames.infestor, [infestation_pit],
        costs = [Mineral(100), Gas(150)])
roach = GameUnit(UnitNames.roach, [roach_warren],
        costs = [Mineral(75), Gas(25)])
baneling = GameUnit(UnitNames.baneling, [baneling_nest],
        costs = [Mineral(25), Gas(25)],
        consumes = [zergling])
brood_lord = GameUnit(UnitNames.brood_lord, [greater_spire],
        costs = [Mineral(150), Gas(150)],
        consumes = [corrupter])


"""
Protoss structures
"""

nexus = GameUnit(UnitNames.nexus)
pylon = GameUnit(UnitNames.pylon)
assimilator = GameUnit(UnitNames.assimilator)
gateway = GameUnit(UnitNames.gateway, [pylon])
cybernetics_core = GameUnit(UnitNames.cybernetics_core, [gateway])
forge = GameUnit(UnitNames.forge, [pylon])
warp_gate = GameUnit(UnitNames.warp_gate, [cybernetics_core])
twilight_council = GameUnit(UnitNames.twilight_council, [cybernetics_core])
templar_archives = GameUnit(UnitNames.templar_archives, [twilight_council])
dark_shrine = GameUnit(UnitNames.dark_shrine, [twilight_council])
stargate = GameUnit(UnitNames.stargate, [cybernetics_core])
fleet_beacon = GameUnit(UnitNames.fleet_beacon, [stargate])
robotics_facility = GameUnit(UnitNames.robotics_facility, [cybernetics_core])
robotics_bay = GameUnit(UnitNames.robotics_bay, [robotics_facility])

"""
Protoss units
"""

probe = GameUnit(UnitNames.probe, [nexus])
zealot = GameUnit(UnitNames.zealot, [gateway])
sentry = GameUnit(UnitNames.sentry, [cybernetics_core])
stalker = GameUnit(UnitNames.stalker, [cybernetics_core])
cannon = GameUnit(UnitNames.cannon, [forge])
dark_templar = GameUnit(UnitNames.dark_templar, [dark_shrine])
high_templar = GameUnit(UnitNames.high_templar, [templar_archives])
phoenix = GameUnit(UnitNames.phoenix, [stargate])
void_ray = GameUnit(UnitNames.void_ray, [stargate])
carrier = GameUnit(UnitNames.carrier, [fleet_beacon])
mothership = GameUnit(UnitNames.mothership, [fleet_beacon])
immortal = GameUnit(UnitNames.immortal, [robotics_facility])
colossus = GameUnit(UnitNames.colossus, [robotics_bay])
observer = GameUnit(UnitNames.observer, [robotics_facility])
warp_prism = GameUnit(UnitNames.warp_prism, [robotics_facility])
