import asyncio
import os

import constants as c
import functions as f

"""
    TODO: 
        * Get the overwriting thing working well.
        * create script / python to kill all active instances?????/
        * Linter
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

os.makedirs(os.path.join('log', 'engines'), exist_ok=True)

gateways = f.create_gateways(8000, 9000, limit=c.NO_ENGINES)
asyncio.run(f.start_simulators(gateways, common_commands))
