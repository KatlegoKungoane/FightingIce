import asyncio
import os

import constants as c
import functions as f

"""
    TODO: 
        * Investigate why we are still using that hpmode stuff in other logs
        * Write all logs into respective experiment folder name
        * Get the overwriting thing working well.
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
	# '--config-path',
	# '1',
	# 'zen',
	# './custom_motions/zen.csv',
	# This is for the ai, so maybe turn on when you have those configured
	# '--headless-mode',
	'--input-sync',
	# '--lightweight-mode',
	'--pyftg-mode',
	'--non-delay',
	'2',
]

print(f'Java jar command:{" ".join(common_commands)}')

os.makedirs(os.path.join('log', 'engines', f'{c.EXPERIMENT_NAME}'), exist_ok=True)

gateways = f.create_gateways(8000, 9000, limit=c.NO_ENGINES)
asyncio.run(f.start_simulators(gateways, common_commands))
