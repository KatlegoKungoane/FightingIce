import asyncio
import os
import numpy as np

import constants as c
import functions as f
import MotionClasses.MotionEditor as me
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

print(f'Java jar command:{" ".join(common_commands)}')

c.POLL_INTERVAL_SEC = 0
asyncio.run(
    f.start_simulators(
        1,
        common_commands,
        characters=np.array([
            [c.CHARACTERS.ZEN.name, c.CHARACTERS.GARNET.name],
            [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
            [c.CHARACTERS.GARNET.name, c.CHARACTERS.LUD.name],
        ], dtype=object),
        motions=me.DEFAULT_MOTION_LIST,
        agent_names=np.full(shape=(3, 2), fill_value=c.AgentNames.MCTS_AGENT),
        experiment_name=f'runner_{f.get_current_time_str(delimiter='.')}',
        # deterministic=deterministic, really dont care
        extra_commands=None,
    )
)
