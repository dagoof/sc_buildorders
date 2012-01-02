import functools, operator, itertools
import decorators

all_gameunits = {}

def register_gameunit(unit):
    all_gameunits[str(unit)] = unit

class GameResource(object):
    @classmethod
    def combine_resources(cls, *resources):
        return cls(sum(r.amount for r in resources if isinstance(r, cls)))
        #return cls(sum(map(operator.attrgetter('amount'),
            #filter(functools.partial(
                #decorators.reverse_args(isinstance), cls),
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
    def __init__(self, name, reqs = (), costs = (),
            consumes = (), acts_as = (), yields = ()):
        self.name = name
        self._reqs = reqs
        self._costs = costs
        self._consumes = consumes
        self._acts_as = acts_as
        self._yields = yields
        self._deps = []
        register_gameunit(self)
        for req in self._reqs:
            req.register_dependent(self)

    def register_dependent(self, other):
        if other not in self._deps:
            self._deps.append(other)

    def valid_with_respect_to(self, active, available):
        if self.consumes and not self.consumes_with_respect_to(active):
            return False
        for more in self.consumes_with_respect_to(active):
            if more not in active:
                return False
        for req in self.requirements:
            if req not in available:
                return False
        return True

    @property
    def requirements(self):
        return self._reqs

    @property
    @decorators.apply_f(list)
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
    @decorators.apply_f(list)
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

    @decorators.apply_f(list)
    def consumes_with_respect_to(self, active):
        def can_remove_each(_remove_from, removed):
            remove_from = _remove_from[:]
            for elem in removed:
                if elem in remove_from:
                    remove_from.remove(elem)
                else:
                    return False
            return True
        active_contains = functools.partial(operator.contains, active)
        if any(map(decorators.is_iterable, self.consumes)):
            for sub in self.consumes:
                if decorators.is_iterable(sub):
                    if can_remove_each(active, sub):
                        for more in sub:
                            yield more
                else:
                    if can_remove_each(active, [sub]):
                        yield sub
        else:
            if can_remove_each(active, self.consumes):
                for more in self.consumes:
                    yield more

    @property
    def yields(self):
        return self._yields

    @property
    @decorators.apply_f(list)
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
    def acts_as(self):
        sofar = [self]
        for unit in self._acts_as:
            for more in unit.acts_as:
                if more not in sofar:
                    sofar.append(more)
        return sofar

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

class RefundUnit(GameUnit):
    def __init__(self, *args, **kwargs):
        super(RefundUnit, self).__init__(*args, **kwargs)
        self._yields = []
        for sub in self.consumes:
            for more in sub.consumes:
                self._yields.append(more)

@decorators.apply_f(list)
def unit_wrapper(unit):
    if unit.yields:
        for more in unit.yields:
            yield more
    else:
        yield unit

class UnitNames:
    hatchery = 'Hatchery'
    drone = 'Drone'
    overlord = 'Overlord'
    extractor = 'Extractor'
    spawning_pool = 'Spawning Pool'
    evolution_chamber = 'Evolution Chamber'
    spore_crawler = 'Spore Crawler'
    spine_crawler = 'Spine Crawler'
    zergling = 'Zergling'
    queen = 'Queen'
    baneling_nest = 'Baneling Nest'
    baneling = 'Baneling'
    roach_warren = 'Roach Warren'
    roach = 'Roach'
    lair = 'Lair'
    overseer = 'Overseer'
    nydus_network = 'Nydus Network'
    nydus_worm = 'Nydus Worm'
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
    gateway = 'Gateway'
    zealot = 'Zealot'
    sentry = 'Sentry'
    stalker = 'Stalker'
    cybernetics_core = 'Cybernetics Core'
    forge = 'Forge'
    photon_cannon = 'Photon Cannon'
    stargate = 'Stargate'
    phoenix = 'Phoenix'
    void_ray = 'Void Ray'
    robotics_facility = 'Robotics Facility'
    robotics_bay = 'Robotics Bay'
    immortal = 'Immortal'
    colossus = 'Colossus'
    observer = 'Observer'
    warp_prism = 'Warp Prism'
    twilight_council = 'Twilight Council'
    templar_archives = 'Templar Archives'
    dark_shrine = 'Dark Shrine'
    high_templar = 'High Templar'
    archon = 'Archon'
    dark_templar = 'Dark Templar'
    fleet_beacon = 'Fleet Beacon'
    mothership = 'Mothership'
    carrier = 'Carrier'

    command_center = 'Command Center'
    scv = 'SCV'
    supply_depot = 'Supply Depot'
    refinery = 'Refinery'
    barracks = 'Barracks'
    tech_lab = 'Tech Lab'
    reactor = 'Reactor'
    engineering_bay = 'Engineering Bay'
    missile_turret = 'Missile Turret'
    marine = 'Marine'
    marauder = 'Marauder'
    reaper = 'Reaper'
    planetary_fortress = 'Planetary Fortress'
    sentry_tower = 'Sentry Tower'
    bunker = 'Bunker'
    factory = 'Factory'
    hellion = 'Hellion'
    siege_tank = 'Siege Tank'
    armory = 'Armory'
    thor = 'Thor'
    orbital_command = 'Orbital Command'
    ghost_academy = 'Ghost Academy'
    ghost = 'Ghost'
    starport = 'Starport'
    viking = 'Viking'
    medivac = 'Medivac'
    banshee = 'Banshee'
    raven = 'Raven'
    fusion_core = 'Fusion Core'
    battlecruiser = 'Battlecruiser'
    tech_lab_barracks = 'Tech Labbed Barracks'
    tech_lab_factory = 'Tech Labbed Factory'
    tech_lab_starport = 'Tech Labbed Starport'
    reactor_barracks = 'Reactored Barracks'
    reactor_factory = 'Reactored Factory'
    reactor_starport = 'Reactored Starport'
    detach_tech_lab_barracks = 'Detach Tech Labbed Barracks'
    detach_tech_lab_factory = 'Detach Tech Labbed Factory'
    detach_tech_lab_starport = 'Detach Tech Labbed Starport'
    detach_reactor_barracks = 'Detach Reactored Barracks'
    detach_reactor_factory = 'Detach Reactored Factory'
    detach_reactor_starport = 'Detach Reactored Starport'

"""
Zerg structures
"""

drone = GameUnit(UnitNames.drone,
        costs = [Mineral(50)])
hatchery = GameUnit(UnitNames.hatchery,
        costs = [Mineral(300)],
        consumes = [drone])
extractor = GameUnit(UnitNames.extractor,
        costs = [Mineral(25)],
        consumes = [drone])
spawning_pool = GameUnit(UnitNames.spawning_pool, [hatchery],
        costs = [Mineral(200)],
        consumes = [drone])
evolution_chamber = GameUnit(UnitNames.evolution_chamber, [hatchery],
        costs = [Mineral(75)],
        consumes = [drone])
spore_crawler = GameUnit(UnitNames.spore_crawler, [evolution_chamber],
        costs = [Mineral(75)],
        consumes = [drone])
spine_crawler = GameUnit(UnitNames.spine_crawler, [spawning_pool],
        costs = [Mineral(100)],
        consumes = [drone])
baneling_nest = GameUnit(UnitNames.baneling_nest, [spawning_pool],
        costs = [Mineral(100), Gas(50)],
        consumes = [drone])
roach_warren = GameUnit(UnitNames.roach_warren, [spawning_pool],
        costs = [Mineral(150)],
        consumes = [drone])
lair = GameUnit(UnitNames.lair, [spawning_pool],
        costs = [Mineral(150), Gas(100)],
        consumes = [hatchery],
        acts_as = [hatchery])
nydus_network = GameUnit(UnitNames.nydus_network, [lair],
        costs = [Mineral(150), Gas(200)],
        consumes = [drone])
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
        consumes = [lair],
        acts_as = [lair])
ultralisk_den = GameUnit(UnitNames.ultralisk_den, [hive],
        costs = [Mineral(150), Gas(200)],
        consumes = [drone])
greater_spire = GameUnit(UnitNames.greater_spire, [hive],
        costs = [Mineral(100), Gas(150)],
        consumes = [spire],
        acts_as = [spire])


"""
Zerg units
"""

overlord = GameUnit(UnitNames.overlord,
        costs = [Mineral(100)])
zergling = GameUnit(UnitNames.zergling, [spawning_pool],
        costs = [Mineral(25)])
overseer = GameUnit(UnitNames.overseer, [lair],
        costs = [Mineral(50), Gas(50)],
        consumes = [overlord],
        acts_as = [overlord])
queen = GameUnit(UnitNames.queen, [spawning_pool],
        costs = [Mineral(150)])
ultralisk = GameUnit(UnitNames.ultralisk, [ultralisk_den],
        costs = [Mineral(300), Gas(200)])
nydus_worm = GameUnit(UnitNames.nydus_worm, [nydus_network],
        costs = [Mineral(100), Gas(100)])
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

nexus = GameUnit(UnitNames.nexus,
        costs = [Mineral(400)])
pylon = GameUnit(UnitNames.pylon,
        costs = [Mineral(100)])
assimilator = GameUnit(UnitNames.assimilator,
        costs = [Mineral(75)])
gateway = GameUnit(UnitNames.gateway, [pylon],
        costs = [Mineral(150)])
cybernetics_core = GameUnit(UnitNames.cybernetics_core, [gateway],
        costs = [Mineral(150)])
forge = GameUnit(UnitNames.forge, [pylon],
        costs = [Mineral(150)])
twilight_council = GameUnit(UnitNames.twilight_council, [cybernetics_core],
        costs = [Mineral(150), Gas(100)])
templar_archives = GameUnit(UnitNames.templar_archives, [twilight_council],
        costs = [Mineral(150), Gas(200)])
dark_shrine = GameUnit(UnitNames.dark_shrine, [twilight_council],
        costs = [Mineral(100), Gas(250)])
stargate = GameUnit(UnitNames.stargate, [cybernetics_core],
        costs = [Mineral(150), Gas(150)])
fleet_beacon = GameUnit(UnitNames.fleet_beacon, [stargate],
        costs = [Mineral(300), Gas(200)])
robotics_facility = GameUnit(UnitNames.robotics_facility, [cybernetics_core],
        costs = [Mineral(200), Gas(100)])
robotics_bay = GameUnit(UnitNames.robotics_bay, [robotics_facility],
        costs = [Mineral(200), Gas(200)])


"""
Protoss units
"""

probe = GameUnit(UnitNames.probe,
        costs = [Mineral(50)])
zealot = GameUnit(UnitNames.zealot, [gateway],
        costs = [Mineral(100)])
sentry = GameUnit(UnitNames.sentry, [cybernetics_core],
        costs = [Mineral])
stalker = GameUnit(UnitNames.stalker, [cybernetics_core],
        costs = [Mineral(125), Gas(50)])
photon_cannon = GameUnit(UnitNames.photon_cannon, [forge],
        costs = [Mineral(150)])
dark_templar = GameUnit(UnitNames.dark_templar, [dark_shrine],
        costs = [Mineral(125), Gas(125)])
high_templar = GameUnit(UnitNames.high_templar, [templar_archives],
        costs = [Mineral(50), Gas(150)])
archon = GameUnit(UnitNames.archon,
        consumes = [
            [high_templar, high_templar],
            [high_templar, dark_templar],
            [dark_templar, dark_templar]])
phoenix = GameUnit(UnitNames.phoenix, [stargate],
        costs = [Mineral(150), Gas(100)])
void_ray = GameUnit(UnitNames.void_ray, [stargate],
        costs = [Mineral(250), Gas(150)])
carrier = GameUnit(UnitNames.carrier, [fleet_beacon],
        costs = [Mineral(350), Gas(250)])
mothership = GameUnit(UnitNames.mothership, [fleet_beacon],
        costs = [Mineral(400), Gas(400)])
immortal = GameUnit(UnitNames.immortal, [robotics_facility],
        costs = [Mineral(250), Gas(100)])
colossus = GameUnit(UnitNames.colossus, [robotics_bay],
        costs = [Mineral(300), Gas(200)])
observer = GameUnit(UnitNames.observer, [robotics_facility],
        costs = [Mineral(25), Gas(75)])
warp_prism = GameUnit(UnitNames.warp_prism, [robotics_facility],
        costs = [Mineral(200)])


"""
Terran Structures
"""

command_center = GameUnit(UnitNames.command_center,
        costs = [Mineral(400)])
supply_depot = GameUnit(UnitNames.supply_depot,
        costs = [Mineral(100)])
refinery = GameUnit(UnitNames.refinery,
        costs = [Mineral(75)])
barracks = GameUnit(UnitNames.barracks, [supply_depot],
        costs = [Mineral(150)])
tech_lab = GameUnit(UnitNames.tech_lab, [barracks],
        costs = [Mineral(50), Gas(25)])
reactor = GameUnit(UnitNames.reactor, [barracks],
        costs = [Mineral(50), Gas(50)])
engineering_bay = GameUnit(UnitNames.engineering_bay, [command_center],
        costs = [Mineral(125)])
missile_turret = GameUnit(UnitNames.missile_turret, [engineering_bay],
        costs = [Mineral(100)])
planetary_fortress = GameUnit(UnitNames.planetary_fortress, [engineering_bay],
        costs = [Mineral(150), Gas(150)],
        consumes = [command_center],
        acts_as = [command_center])
sentry_tower = GameUnit(UnitNames.sentry_tower, [engineering_bay],
        costs = [Mineral(125), Gas(100)])
bunker = GameUnit(UnitNames.bunker, [barracks],
        costs = [Mineral(150)])
factory = GameUnit(UnitNames.factory, [barracks],
        costs = [Mineral(150), Gas(100)])
armory = GameUnit(UnitNames.armory, [factory],
        costs = [Mineral(150), Gas(100)])
orbital_command = GameUnit(UnitNames.orbital_command, [barracks],
        costs = [Mineral(150)],
        consumes = [command_center],
        acts_as = [command_center])
ghost_academy = GameUnit(UnitNames.ghost_academy, [barracks],
        costs = [Mineral(150), Gas(50)])
starport = GameUnit(UnitNames.starport, [factory],
        costs = [Mineral(150), Gas(100)])
fusion_core = GameUnit(UnitNames.fusion_core, [starport],
        costs = [Mineral(150), Gas(100)])

tech_lab_barracks = GameUnit(UnitNames.tech_lab_barracks,
        consumes = [tech_lab, barracks],
        acts_as = [barracks])
reactor_barracks = GameUnit(UnitNames.reactor_barracks,
        consumes = [reactor, barracks],
        acts_as = [barracks])
tech_lab_factory = GameUnit(UnitNames.tech_lab_factory,
        consumes = [tech_lab, factory],
        acts_as = [factory])
reactor_factory = GameUnit(UnitNames.reactor_factory,
        consumes = [reactor, factory],
        acts_as = [factory])
tech_lab_starport = GameUnit(UnitNames.tech_lab_starport,
        consumes = [tech_lab, starport],
        acts_as = [starport])
reactor_starport = GameUnit(UnitNames.reactor_starport,
        consumes = [reactor, starport],
        acts_as = [starport])

detach_reactor_barracks = RefundUnit(UnitNames.detach_reactor_barracks,
        consumes = [reactor_barracks])
detach_tech_lab_barracks = RefundUnit(UnitNames.detach_tech_lab_barracks,
        consumes = [tech_lab_barracks])
detach_reactor_factory = RefundUnit(UnitNames.detach_reactor_factory,
        consumes = [reactor_factory])
detach_tech_lab_factory = RefundUnit(UnitNames.detach_tech_lab_factory,
        consumes = [tech_lab_factory])
detach_reactor_starport = RefundUnit(UnitNames.detach_reactor_starport,
        consumes = [reactor_starport])
detach_tech_lab_starport = RefundUnit(UnitNames.detach_tech_lab_starport,
        consumes = [tech_lab_starport])


"""
Terran Units
"""

scv = GameUnit(UnitNames.scv,
        costs = [Mineral(50)])
marine = GameUnit(UnitNames.marine, [barracks],
        costs = [Mineral(50)])
marauder = GameUnit(UnitNames.marauder, [tech_lab_barracks],
        costs = [Mineral(100), Gas(25)])
reaper = GameUnit(UnitNames.reaper, [tech_lab_barracks],
        costs = [Mineral(50), Gas(50)])
hellion = GameUnit(UnitNames.hellion, [factory],
        costs = [Mineral(100)])
siege_tank = GameUnit(UnitNames.siege_tank, [tech_lab_factory],
        costs = [Mineral(150), Gas(125)])
thor = GameUnit(UnitNames.thor, [tech_lab_factory, armory],
        costs = [Mineral(300), Gas(200)])
ghost = GameUnit(UnitNames.ghost, [tech_lab_barracks, ghost_academy],
        costs = [Mineral(200), Gas(100)])
viking = GameUnit(UnitNames.viking, [starport],
        costs = [Mineral(150), Gas(75)])
medivac = GameUnit(UnitNames.medivac, [starport],
        costs = [Mineral(100), Gas(100)])
banshee = GameUnit(UnitNames.banshee, [tech_lab_starport],
        costs = [Mineral(150), Gas(100)])
raven = GameUnit(UnitNames.raven, [tech_lab_starport],
        costs = [Mineral(100), Gas(200)])
battlecruiser = GameUnit(UnitNames.battlecruiser,
        [tech_lab_starport, fusion_core],
        costs = [Mineral(300), Gas(200)])


zerg_units = [ drone, overlord, hatchery, extractor, spawning_pool,
        evolution_chamber, spore_crawler, spine_crawler, baneling_nest,
        roach_warren, lair, overseer, nydus_network, infestation_pit,
        spire, hydralisk_den, hive, ultralisk_den, greater_spire,
        zergling, queen, ultralisk, nydus_worm, hydralisk, corrupter,
        mutalisk, infestor, roach, baneling, brood_lord ]
protoss_units = [ nexus, pylon, assimilator, gateway, cybernetics_core,
        forge, twilight_council, templar_archives, dark_shrine, stargate,
        fleet_beacon, robotics_facility, robotics_bay, probe, zealot,
        sentry, stalker, photon_cannon, dark_templar, high_templar, archon,
        phoenix, void_ray, carrier, mothership, immortal, colossus,
        observer, warp_prism ]
terran_units = [ command_center, scv, supply_depot, refinery, barracks,
        tech_lab_barracks, tech_lab_factory, tech_lab_starport,
        reactor_barracks, reactor_factory, reactor_starport,
        detach_tech_lab_barracks, detach_tech_lab_factory,
        detach_tech_lab_starport,
        tech_lab, reactor, engineering_bay, missile_turret, marine,
        marauder, reaper, planetary_fortress, sentry_tower, bunker, factory,
        hellion, siege_tank, armory, thor, orbital_command, ghost_academy,
        ghost, starport, viking, medivac, banshee, raven, fusion_core,
        battlecruiser ]

class Races:
    ZERG = 'zerg'
    TERRAN = 'terran'
    PROTOSS = 'protoss'
