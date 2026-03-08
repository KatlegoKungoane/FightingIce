import datetime
import os

NO_GAMES: int = 1
NO_ENGINES: int = 1
PLAYER_HP: int = 400
POLL_INTERVAL_SEC: int = 1
GAME_DURATION_SEC: int = 60
EXPERIMENT_NAME: str = 'adhoc'
ZIP_FILES: bool = True

KNOWN_LOGS: list[str] = [
	'engines',
	'frameData',
	'motions',
	'point',
	'replay',
	'sound',  # We dont really use this though...
]

GAME_TIME: str = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')


class CHARACTERS:
	ZEN = 'ZEN'
	GARNET = 'GARNET'
	LUD = 'LUD'
 

CHARACTER_MOTION_PATHS: list[str | None] = [
	None,
	None,
]

DEFAULT_MOTIONS_PATH: str = os.path.join('data', 'characters')

class PointHeaderNames:
	INSTANCE = 'instance'
	ROUND = 'round' 
	HP_ONE = 'hp_one' 
	HP_TWO = 'hp_two' 
	DRAIN = 'drain' 
	WINNER = 'winner' 
	SIMULATION_NUMBER = 'simulation_number'

	D_TYPE = {
		INSTANCE: 'int16',
		ROUND: 'int16',
		HP_ONE: 'int16',
		HP_TWO: 'int16',
		DRAIN: 'int16',
		WINNER: 'int16',
	}