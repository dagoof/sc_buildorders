import functools

def convert_to(conversion_target):
    def decorator(f):
        @functools.wraps(f)
        def _wrapped(*args, **kwargs):
            return conversion_target(f(*args, **kwargs))
        return _wrapped
    return decorator

class GameUnit(object):
    def __init__(self, name, reqs = (), costs = ()):
        self.name = name
        self._reqs = reqs
        self._costs = costs
        self._deps = []
        for req in self._reqs:
            req.register_dependent(self)

    def register_dependent(self, other):
        if other not in self._deps:
            self._deps.append(other)

    @property
    def immediate_requirements(self):
        return self._reqs

    @property
    @convert_to(list)
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
    def available_choices(self):
        return self._deps

    def __repr__(self):
        return '<{_class}: {_name}>'.format(_name = self.name,
                _class = self.__class__.__name__)

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

hatchery = GameUnit(UnitNames.hatchery)
spawning_pool = GameUnit(UnitNames.spawning_pool)
baneling_nest = GameUnit(UnitNames.baneling_nest, [spawning_pool])
roach_warren = GameUnit(UnitNames.roach_warren, [spawning_pool])
lair = GameUnit(UnitNames.lair, [spawning_pool])
infestation_pit = GameUnit(UnitNames.infestation_pit, [lair])
spire = GameUnit(UnitNames.spire, [lair])
hydralisk_den = GameUnit(UnitNames.hydralisk_den, [lair])
hive = GameUnit(UnitNames.hive, [infestation_pit])
ultralisk_den = GameUnit(UnitNames.ultralisk_den, [hive])
greater_spire = GameUnit(UnitNames.greater_spire, [hive, spire])


"""
Zerg units
"""

drone = GameUnit(UnitNames.drone, [hatchery])
zergling = GameUnit(UnitNames.zergling, [spawning_pool])
ultralisk = GameUnit(UnitNames.ultralisk, [ultralisk_den])
hydralisk = GameUnit(UnitNames.hydralisk, [hydralisk_den])
corrupter = GameUnit(UnitNames.corrupter, [spire])
mutalisk = GameUnit(UnitNames.mutalisk, [spire])
infestor = GameUnit(UnitNames.infestor, [infestation_pit])
roach = GameUnit(UnitNames.roach, [roach_warren])
baneling = GameUnit(UnitNames.baneling, [baneling_nest])
brood_lord = GameUnit(UnitNames.brood_lord, [corrupter, greater_spire])


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
