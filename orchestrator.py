import asyncio
import datetime
import os

import constants as c
import functions as f
from MotionClasses.MotionEditor import MotionEditor
from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names

"""
    TODO: 
		* Maybe look into consolidating when you are orchestrating many tournaments
		* IMPORTANT IMPORTANT!!!! The replay is a key press replay, not a video... meaning you need to remember the motions
        * Get the overwriting thing working well.
        * Linter
        * create script / python to kill all active instances?????
			* Don't remember what this is
		* Investigate way to record multiple matches on multiple screens.
		* I'm sure we can get the frames themselves then draw.
		* Especially because the replay is just a recording of steps per frame, meaning that different meta states affect the efficacy.
"""

"""
	The objective right now is to have an orchestrator
	it can do everything in 1 shot. But I think we will maybe do it in parts.
	we will first setup an env where we incrementally increase Zen's kick range over 10 simulations, then afterwards, we will see how that affects win rate.
	Maybe we can consider using jupyter :new_moon
"""


async def start_orchestration(deterministic: bool = True) -> None:
	for i in range(1):
		c.GAME_TIME = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')
		base_experiment_name = 'non_deterministic_ai_1'
		experiment_name = f'{base_experiment_name}_{i}'

		custom_motion_file_name_zen = os.path.join(
			'custom_motions',
			base_experiment_name,
			f'zen_{i}.csv',
		)

		zen_motion_editor = MotionEditor(
			c.CHARACTERS.ZEN,
			custom_motion_file_name_zen,
		)

		garnet_motion_editor = MotionEditor(
			c.CHARACTERS.GARNET,
			custom_motion_path=None,
		)

		zen_motion_editor.motion_custom.at[
			motion_names.STAND_B,
			headers.ATTACK_HIT_AREA_RIGHT,
		] += i * 5

		zen_motion_editor.save_custom_motion()

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
			'--config-path',
			'1',
			'zen',
			zen_motion_editor.custom_motion_path,
			# This is for the ai, so maybe turn on when you have those configured
			#'--headless-mode',
			'--input-sync',
			#'--lightweight-mode',
			'--pyftg-mode',
			'--non-delay',
			'2',
		]

		print(f'Java jar command:{" ".join(common_commands)}')

		os.makedirs(os.path.join('log', 'engines'), exist_ok=True)

		gateways = f.create_gateways(8000, 9000, limit=c.NO_ENGINES)
		await f.start_simulators(
			gateways,
			common_commands,
			[
				c.CHARACTERS.ZEN,
				c.CHARACTERS.GARNET,
			],
			[
				zen_motion_editor.motion_custom,
				garnet_motion_editor.motion_default,
			],
			experiment_name,
			deterministic=deterministic
		)


if __name__ == '__main__':
	# c.GAME_TIME = c.GAME_TIME
	# c.GAME_DURATION_SEC = c.GAME_DURATION_SEC
	# c.PLAYER_HP = c.PLAYER_HP
	c.NO_ENGINE = 1
	c.NO_GAMES = 1
	asyncio.run(start_orchestration(deterministic=False))
