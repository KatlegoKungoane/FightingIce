import datetime
import os
from enum import Enum

NO_GAMES: int = 1
NO_ENGINES: int = 1
PLAYER_HP: int = 400
PLAYER_MAX_ENERGY: int = 300
POLL_INTERVAL_SEC: int = 1
GAME_DURATION_SEC: int = 60
EXPERIMENT_NAME: str = 'adhoc'
ZIP_FILES: bool = True

DEFAULT_MOTIONS_PATH: str = os.path.join('data', 'characters')
MOTIONS_FILE_NAME: str = 'Motion.csv'
CUSTOM_MOTION_PATH: str = 'custom_motions'

KNOWN_LOGS: list[str] = [
    'engines',
    'frameData',
    'motions',
    'point',
    'replay',
    'sound',  # We dont really use this though...
]

GAME_TIME: str = datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S')


class CHARACTERS(Enum):
    ZEN: str = 'ZEN'
    GARNET: str = 'GARNET'
    LUD: str = 'LUD'

CHARACTER_ORDER: dict[str, int] = {
    CHARACTERS.ZEN.name: 0,
    CHARACTERS.GARNET.name: 1,
    CHARACTERS.LUD.name: 2,
}

CHARACTER_ORDER_REVERSE: dict[int, str] = {
    0: CHARACTERS.ZEN.name,
    1: CHARACTERS.GARNET.name,
    2: CHARACTERS.LUD.name,
}


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


class AgentNames:
    MCTS_AGENT = 'MctsAi23i'
    KAT_KICK_AI = 'kat kick'

class ScreenDimensions:
    WIDTH: int = 960
    HEIGHT: int = 640


class MotionData:
    rows: int = 56
    cols: int = 33
    shape: tuple[int, int] = (rows, cols)

class pymoo:
    class TERMINATION:
        EVALUATION_LIMIT = 'n_eval'
        GENERATION_LIMIT = 'n_gen'
        OBJECTIVE_THRESHOLD = 'fmin'
        TIME_LIMIT = 'time'

    class MOEAD:
        class SpreadType:
            UNIFORM: str = "uniform"
            DAS_DENNIS: str = "das-dennis"
            ENERGY: str = "energy"
            MULTI_LAYER: str = "multi-layer"
            LAYER_ENERGY: str = "layer-energy"
            REDUCTION: str = "reduction"
            INCREMENTAL: str = "incremental"