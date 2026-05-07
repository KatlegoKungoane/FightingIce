import asyncio
import numpy as np
import os

from pyftg.socket.aio.gateway import Gateway
import MotionClasses.MotionEditor as me
from MotionClasses.MotionNames import MotionNames as motion_names
from MotionClasses.MotionHeaders import MotionHeaders as headers
import GeneticAlgorithm.genetic_functions as gf

import constants as c
import functions as f

"""
	Objective of this file
		We are trying to simulate x games, ran over multiple simulators.
		Maybe we can pass in who's playing who, and where the motions are.
"""

"""
    TODO:
        * Get the overwriting thing working well.
        * Linter
        * create script / python to kill all active instances?????
			* Don't remember what this is
"""


f.arg_parser()

common_commands = [
    'java',
    '-cp',
    os.pathsep.join(['dare.jar', '.']),
    'Main',
    '--limithp',
    str(c.PLAYER_HP),
    str(c.PLAYER_HP),
    # '--slow',
    '-df',
    '-r',
    '1',
    '-f',
    str(c.GAME_DURATION_SEC * 60),
    '--time-stamp',
    c.GAME_TIME,
    # '--config-path',
    # '1',
    # 'zen',
    # './custom_motions/zen.csv',
    # This is for the ai, so maybe turn on when you have those configured
    '--headless-mode',
    '--input-sync',
    '--lightweight-mode',
    '--pyftg-mode',
    '--non-delay',
    '2',
]

motion_adjustments: list[tuple[str, str]] = [
    (motion_names.STAND_A, headers.ATTACK_HIT_DAMAGE),
    (motion_names.STAND_B, headers.ATTACK_HIT_DAMAGE),
]

motion_coordinates: np.ndarray = gf.get_motion_coordinates(motion_adjustments)
gene = np.array([24, 167])

mutated_motions = gf.gene_to_motions(gene=gene, motion_coordinates=motion_coordinates)
experiment_name: str = f.append_time_uuid_experiment('runner')

custom_motion_paths: list[str] = [
    os.path.join(
        c.CUSTOM_MOTION_PATH,
        experiment_name,
        f'{character_name.lower()}.csv',
    )  #
    for character_name in c.CHARACTER_ORDER.keys()
]

for path, mutated_motion in zip(custom_motion_paths, mutated_motions, strict=True):
    me.save_custom_motion(
        motion=mutated_motion,
        path=path,
    )

argument_for_custom_motions: np.ndarray = np.full(shape=(3, 6), dtype=object, fill_value='')
# character_order_combinations: list[tuple[int, int]] = list(combinations([0, 1, 2], 2))
# Custom match-ups
character_order_combinations: list[tuple[int, int]] = [
    (0, 2),
    (0, 2),
    (0, 2),
]
for index, combination in enumerate(character_order_combinations):
    argument_for_custom_motions[index, :] = np.array(
        [
            '--config-path',
            '2',
            c.CHARACTER_ORDER_REVERSE[combination[0]],
            custom_motion_paths[combination[0]],
            c.CHARACTER_ORDER_REVERSE[combination[1]],
            custom_motion_paths[combination[1]],
        ]
    )

print(f'Java jar command:{" ".join(common_commands)}')

# port: int | None = 61254

# gateway = Gateway(port=port)

c.POLL_INTERVAL_SEC = 0
# experiment_name: str = 'runner_06.50.57'
c.NO_GAMES = 5
c.CORES = 6
experiment_name: str = f'runner_{f.get_current_time_str(delimiter='.')}'
asyncio.run(
    # gateway.run_game(
    #     ['test_mcts<name>ZEN', 'GARNET'],
    #     [c.AgentNames.KAT_MCTS_AGENT, c.AgentNames.MCTS_AGENT],
    #     1,
    # )
    f.start_simulators(
        6,
        common_commands,
        characters=np.array([
            [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
            [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
            [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
        ], dtype=object),
        motions=me.DEFAULT_MOTION_LIST,
        agent_names=np.full(shape=(3, 2), fill_value=c.AgentNames.MCTS_AGENT),
        experiment_name=experiment_name,
        # deterministic=deterministic, really dont care
        extra_commands=argument_for_custom_motions,
    )

)
f.consolidate_data(experiment_name)

excitement = asyncio.run(gf.calculate_excitement(experiment_name, frame_window=10))
print(excitement)