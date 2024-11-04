import os
import random
import logging
import argparse
from typing import List, Dict, Set
import datetime

os.environ["SC2PATH"] = "W:/StarCraft II"

from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2 import maps
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.position import Point2
from sc2.unit import Unit

class ImprovedTerranBot(BotAI):
    def __init__(self):
        super().__init__()
        self.attack_groups: Dict[UnitTypeId, Set[int]] = {}
        self.expand_interval: int = 180
        self.last_expand_time: int = 0
        self.combatUnits = {UnitTypeId.MARINE, UnitTypeId.MARAUDER, UnitTypeId.SIEGETANK, UnitTypeId.MEDIVAC, UnitTypeId.VIKINGFIGHTER, UnitTypeId.LIBERATOR, UnitTypeId.REAPER}
        self.scout_sent = False
        self.enemy_air_units_detected = False
        self.max_workers = 70
        self.desired_gas_workers = 3
        self.max_command_centers = 5
        self.last_attack_time = 0
        self.attack_interval = 120
        self.expansion_distances = [20, 15, 10, 5]
        self.surrender_threshold = 0.3
        self.last_townhall_check = 0
        self.townhall_check_interval = 60
        self.max_refineries = 8
        self.max_factories = 3
        self.unit_tags_received_action = set()
        self.early_game_threshold = 300  # 5 minutes
        self.mid_game_threshold = 600  # 10 minutes
        self.scouting_interval = 60  # Scout every 60 seconds
        self.last_scout_time = 0
        self.enemy_build = "Unknown"
        self.enemy_expansions = set()
        self.log_interval = 100  # Log every 100 iterations
        
        self.desired_army_composition = {
            UnitTypeId.MARINE: 0.5,
            UnitTypeId.MARAUDER: 0.2,
            UnitTypeId.SIEGETANK: 0.15,
            UnitTypeId.MEDIVAC: 0.1,
            UnitTypeId.VIKINGFIGHTER: 0.05
        }
        self.max_army_supply = 120
        self.supply_buffer = 6

    async def on_start(self):
        self.client.game_step = 2
        await self.chat_send("GL HF!")

    async def on_step(self, iteration: int):
        try:
            await self.distribute_workers()
            await self.manage_supply()
            await self.manage_economy()
            await self.manage_production()
            await self.manage_army()
            await self.manage_upgrades()
            await self.execute_scouting()
            await self.check_enemy_air_transition()

            if iteration % self.log_interval == 0:
                await self.log_game_state(iteration)

        except Exception as e:
            print(f"Error in on_step: {str(e)}")
            import traceback
            print(traceback.format_exc())

    async def manage_supply(self):
        if self.supply_left < self.supply_buffer and not self.already_pending(UnitTypeId.SUPPLYDEPOT):
            if self.can_afford(UnitTypeId.SUPPLYDEPOT):
                await self.build(UnitTypeId.SUPPLYDEPOT, near=self.townhalls.random.position.towards(self.game_info.map_center, 5))

    async def manage_economy(self):
        await self.expand()
        await self.manage_workers()
        await self.manage_gas()

    async def expand(self):
        if (self.townhalls.amount < min(self.time / 180, self.max_command_centers) and
            self.can_afford(UnitTypeId.COMMANDCENTER) and
            not self.already_pending(UnitTypeId.COMMANDCENTER)):
            await self.expand_now()

    async def manage_workers(self):
        if self.workers.amount < min(self.townhalls.amount * 22, self.max_workers):
            for cc in self.townhalls.ready.idle:
                if self.can_afford(UnitTypeId.SCV):
                    await self.do(cc.train(UnitTypeId.SCV))

    async def manage_gas(self):
        if self.vespene < self.minerals / 2:
            if self.can_afford(UnitTypeId.REFINERY) and self.units(UnitTypeId.REFINERY).amount < min(self.townhalls.amount * 2, self.max_refineries):
                for th in self.townhalls.ready:
                    vgs = self.state.vespene_geyser.closer_than(10, th)
                    for vg in vgs:
                        if not self.units(UnitTypeId.REFINERY).closer_than(1, vg).exists:
                            worker = self.select_build_worker(vg.position)
                            if worker:
                                await self.do(worker.build(UnitTypeId.REFINERY, vg))
                                return  # Build one refinery at a time

    async def manage_production(self):
        await self.build_production_structures()
        await self.produce_units()

    async def build_production_structures(self):
        if self.units(UnitTypeId.BARRACKS).ready.exists:
            if self.units(UnitTypeId.FACTORY).amount < min(self.townhalls.amount, self.max_factories) and self.can_afford(UnitTypeId.FACTORY):
                await self.build(UnitTypeId.FACTORY, near=self.townhalls.random.position.towards(self.game_info.map_center, 8))
            if self.units(UnitTypeId.STARPORT).amount < 2 and self.can_afford(UnitTypeId.STARPORT):
                await self.build(UnitTypeId.STARPORT, near=self.townhalls.random.position.towards(self.game_info.map_center, 10))
        
        # Add more Barracks as the game progresses
        if self.townhalls.amount >= 2 and self.can_afford(UnitTypeId.BARRACKS) and self.units(UnitTypeId.BARRACKS).amount < 8:
            await self.build(UnitTypeId.BARRACKS, near=self.townhalls.random.position.towards(self.game_info.map_center, 8))

        # Build add-ons
        for barracks in self.units(UnitTypeId.BARRACKS).ready:
            if not barracks.has_add_on and self.can_afford(UnitTypeId.BARRACKSTECHLAB):
                await self.do(barracks.build(UnitTypeId.BARRACKSTECHLAB))

        for factory in self.units(UnitTypeId.FACTORY).ready:
            if not factory.has_add_on and self.can_afford(UnitTypeId.FACTORYTECHLAB):
                await self.do(factory.build(UnitTypeId.FACTORYTECHLAB))

        for starport in self.units(UnitTypeId.STARPORT).ready:
            if not starport.has_add_on and self.can_afford(UnitTypeId.STARPORTTECHLAB):
                await self.do(starport.build(UnitTypeId.STARPORTTECHLAB))

    async def produce_units(self):
        if self.supply_army < self.max_army_supply:
            for unit_type, desired_ratio in self.desired_army_composition.items():
                desired_count = int(self.max_army_supply * desired_ratio)
                current_count = self.units(unit_type).amount
                
                if current_count < desired_count:
                    if unit_type == UnitTypeId.MARINE:
                        for barracks in self.units(UnitTypeId.BARRACKS).ready.idle:
                            if self.can_afford(UnitTypeId.MARINE):
                                await self.do(barracks.train(UnitTypeId.MARINE))
                    elif unit_type == UnitTypeId.MARAUDER:
                        for barracks in self.units(UnitTypeId.BARRACKS).ready.idle:
                            if self.can_afford(UnitTypeId.MARAUDER) and barracks.has_add_on:
                                await self.do(barracks.train(UnitTypeId.MARAUDER))
                    elif unit_type == UnitTypeId.SIEGETANK:
                        for factory in self.units(UnitTypeId.FACTORY).ready.idle:
                            if self.can_afford(UnitTypeId.SIEGETANK) and factory.has_add_on:
                                await self.do(factory.train(UnitTypeId.SIEGETANK))
                    elif unit_type in {UnitTypeId.MEDIVAC, UnitTypeId.VIKINGFIGHTER}:
                        for starport in self.units(UnitTypeId.STARPORT).ready.idle:
                            if self.can_afford(unit_type):
                                await self.do(starport.train(unit_type))

    async def manage_army(self):
        army = self.units.of_type(self.combatUnits)
        if army.amount > 50 or (self.time - self.last_attack_time > self.attack_interval and army.amount > 35):
            await self.attack()
        else:
            await self.defend()

    async def attack(self):
        target = await self.select_target()
        
        for tank in self.units(UnitTypeId.SIEGETANK):
            await self.do(tank(AbilityId.SIEGEMODE_SIEGEMODE))
        
        for unit in self.units.of_type(self.combatUnits):
            await self.do(unit.attack(target))
        
        self.last_attack_time = self.time
        print(f"Launching attack with {self.units.of_type(self.combatUnits).amount} units at time {self.time}")

    async def defend(self):
        defensive_position = self.start_location.towards(self.game_info.map_center, 10)
        for unit in self.units.of_type(self.combatUnits):
            await self.do(unit.attack(defensive_position))

    async def select_target(self):
        if self.known_enemy_structures.exists:
            return self.known_enemy_structures.random.position
        elif self.enemy_start_locations:
            return random.choice(self.enemy_start_locations)
        return self.game_info.map_center

    async def manage_upgrades(self):
        if self.units(UnitTypeId.ENGINEERINGBAY).ready.exists:
            eb = self.units(UnitTypeId.ENGINEERINGBAY).ready.first
            if self.can_afford(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1):
                await self.do(eb.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1))
            elif self.can_afford(UpgradeId.TERRANINFANTRYARMORSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANINFANTRYARMORSLEVEL1):
                await self.do(eb.research(UpgradeId.TERRANINFANTRYARMORSLEVEL1))

        if self.units(UnitTypeId.ARMORY).ready.exists:
            armory = self.units(UnitTypeId.ARMORY).ready.first
            if self.can_afford(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1):
                await self.do(armory.research(UpgradeId.TERRANVEHICLEWEAPONSLEVEL1))
            elif self.can_afford(UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL1) and not self.already_pending_upgrade(UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL1):
                await self.do(armory.research(UpgradeId.TERRANVEHICLEANDSHIPARMORSLEVEL1))

    async def execute_scouting(self):
        if self.time - self.last_scout_time > self.scouting_interval:
            if self.units(UnitTypeId.MARINE).exists:
                scout = self.units(UnitTypeId.MARINE).random
                target = random.choice(list(self.expansion_locations))
                await self.do(scout.move(target))
                self.last_scout_time = self.time

    async def check_enemy_air_transition(self):
        if self.known_enemy_structures(UnitTypeId.STARPORT).exists or self.known_enemy_units.of_type({UnitTypeId.MUTALISK, UnitTypeId.VOIDRAY, UnitTypeId.CARRIER}).exists:
            self.enemy_air_units_detected = True

    async def log_game_state(self, iteration):
        game_state = f"""
Iteration: {iteration}
Time: {self.time:.2f}
Resources: Minerals: {self.minerals}, Vespene: {self.vespene}
Supply: {self.supply_used}/{self.supply_cap}
Workers: {self.workers.amount} (Ideal: {self.townhalls.amount * 22})
Army Supply: {self.supply_army}
Structures: CC: {self.townhalls.amount}, Rax: {self.units(UnitTypeId.BARRACKS).amount}, Fac: {self.units(UnitTypeId.FACTORY).amount}, Port: {self.units(UnitTypeId.STARPORT).amount}
Army: Marines: {self.units(UnitTypeId.MARINE).amount}, Marauders: {self.units(UnitTypeId.MARAUDER).amount}, Tanks: {self.units(UnitTypeId.SIEGETANK).amount}, Medivacs: {self.units(UnitTypeId.MEDIVAC).amount}, Vikings: {self.units(UnitTypeId.VIKINGFIGHTER).amount}
Enemy Air Detected: {self.enemy_air_units_detected}
Last Attack Time: {self.last_attack_time:.2f}
        """
        print(game_state)

def run_game_with_bot(map_name, opponent_races, difficulties, num_opponents, realtime=False):
    players = [Bot(Race.Terran, ImprovedTerranBot())]
    
    for i in range(num_opponents):
        players.append(Computer(opponent_races[i], difficulties[i]))
    
    result = run_game(
        maps.get(map_name),
        players,
        realtime=realtime,
        save_replay_as=f"my_bot_game_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.SC2Replay"
    )
    return result

def run_benchmark(num_matches, map_name, opponent_races, difficulties, num_opponents):
    results = {
        'wins': 0,
        'losses': 0,
        'total_time': 0
    }

    output_filename = f"benchmark_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(output_filename, 'w') as output_file:
        output_file.write(f"Benchmark started at {datetime.datetime.now()}\n")
        output_file.write(f"Map: {map_name}\n")
        output_file.write(f"Number of matches: {num_matches}\n")
        output_file.write(f"Number of opponents: {num_opponents}\n")
        output_file.write(f"Opponent races: {[race.name for race in opponent_races]}\n")
        output_file.write(f"Difficulties: {[diff.name for diff in difficulties]}\n\n")

        for match in range(num_matches):
            output_file.write(f"Starting match {match+1} of {num_matches}\n")
            output_file.flush()
            print(f"Starting match {match+1} of {num_matches}")

            try:
                result = run_game_with_bot(map_name, opponent_races, difficulties, num_opponents)

                if result is None:
                    output_file.write(f"Match {match+1} resulted in None. Skipping this match.\n")
                    output_file.flush()
                    print(f"Match {match+1} resulted in None. Skipping this match.")
                    continue

                match_result, match_time = result
                if match_result == 'Victory':
                    results['wins'] += 1
                else:
                    results['losses'] += 1

                results['total_time'] += match_time
                output_file.write(f"Match {match+1} result: {match_result}, Duration: {match_time}\n")
                output_file.flush()
                print(f"Match {match+1} result: {match_result}, Duration: {match_time}")

            except Exception as e:
                output_file.write(f"Error in match {match+1}: {str(e)}\n")
                output_file.flush()
                print(f"Error in match {match+1}: {str(e)}")

            # Write current results after each match
            avg_time = results['total_time'] / (match + 1)
            current_summary = f"\nCurrent results:\nWins: {results['wins']}\nLosses: {results['losses']}\nAvg Time: {avg_time:.2f}\n"
            output_file.write(current_summary)
            output_file.flush()

        avg_time = results['total_time'] / num_matches if num_matches > 0 else 0
        summary = f"\nBenchmark completed.\nWins: {results['wins']}\nLosses: {results['losses']}\nAvg Time: {avg_time:.2f}"
        output_file.write(summary)
        output_file.flush()
        print(summary)
        print(f"Benchmark results written to {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Run ImprovedTerranBot in StarCraft II")
    parser.add_argument("--run-matches", type=int, help="Number of matches to run for benchmarking")
    parser.add_argument("--num-opponents", type=int, default=1, help="Number of opponents")
    parser.add_argument("--difficulties", type=str, nargs='+', choices=['Easy', 'Medium', 'Hard', 'VeryHard', 'CheatVision', 'CheatMoney', 'CheatInsane'], default=['Hard'], help="AI difficulties")
    parser.add_argument("--races", type=str, nargs='+', choices=['Terran', 'Zerg', 'Protoss', 'Random'], default=['Random'], help="Opponent races")
    parser.add_argument("--map", type=str, default="AcropolisLE", help="Map name")
    args = parser.parse_args()

    # Ensure the number of difficulties and races match the number of opponents
    if len(args.difficulties) < args.num_opponents:
        args.difficulties *= args.num_opponents
    if len(args.races) < args.num_opponents:
        args.races *= args.num_opponents
    
    difficulties = [getattr(Difficulty, diff) for diff in args.difficulties[:args.num_opponents]]
    races = [getattr(Race, race) for race in args.races[:args.num_opponents]]

    if args.run_matches:
        run_benchmark(args.run_matches, args.map, races, difficulties, args.num_opponents)
    else:
        result = run_game_with_bot(args.map, races, difficulties, args.num_opponents, realtime=False)
        # Write single game result to a file
        output_filename = f"game_result_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_filename, 'w') as output_file:
            output_file.write(f"Game result: {result}\n")
        print(f"Game result written to {output_filename}")

if __name__ == "__main__":
    main()