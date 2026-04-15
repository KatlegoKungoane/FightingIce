from typing import TypedDict
import numpy as np
import pandas
import os
from itertools import combinations
import pathlib
from datetime import datetime
import time
import asyncio

import constants as c
import functions as f

import MotionClasses.MotionEditor as me
import MotionClasses.MotionHeaders as mh
import MotionClasses.MotionNames as mn


# According to research, its just euclid distance between objects
# TODO parallelize
def constraint_novelty_search(
    numerical_motions: np.ndarray,
    string_motions: np.ndarray | None,
    boolean_motions: np.ndarray | None,
) -> float:
    numerical_motions_slice = numerical_motions.copy()[:, :, me.ConstraintInformation.utilized_numerical_cols]
    num_zen_garnet_distance = np.linalg.norm(numerical_motions_slice[0] - numerical_motions_slice[1])
    num_zen_lud_distance = np.linalg.norm(numerical_motions_slice[0] - numerical_motions_slice[2])
    num_garnet_lud_distance = np.linalg.norm(numerical_motions_slice[1] - numerical_motions_slice[2])

    if string_motions is None:
        str_zen_garnet_distance = 0
        str_zen_lud_distance = 0
        str_garnet_lud_distance = 0
    else:
        str_zen_garnet_distance = np.linalg.norm((string_motions[0] != string_motions[1]).astype(int))
        str_zen_lud_distance = np.linalg.norm((string_motions[0] != string_motions[2]).astype(int))
        str_garnet_lud_distance = np.linalg.norm((string_motions[1] != string_motions[2]).astype(int))

    if boolean_motions is None:
        bool_zen_garnet_distance = 0
        bool_zen_lud_distance = 0
        bool_garnet_lud_distance = 0
    else:
        bool_zen_garnet_distance = np.linalg.norm((boolean_motions[0] != boolean_motions[1]).astype(int))
        bool_zen_lud_distance = np.linalg.norm((boolean_motions[0] != boolean_motions[2]).astype(int))
        bool_garnet_lud_distance = np.linalg.norm((boolean_motions[1] != boolean_motions[2]).astype(int))

    # Adding a normalization to the uniqueness constraint
    numerical_normalization: float = (
        me.ConstraintInformation.THEORETICAL_MAX_NUMERICAL_UNIQUENESS_SINGLE_ROW  #
        * numerical_motions.shape[1]
    )

    str_normalization: float = (
        1  #
        if string_motions is None
        else string_motions.shape[1] * string_motions.shape[2]
    )

    bool_normalization: float = (
        1  #
        if boolean_motions is None
        else boolean_motions.shape[1] * boolean_motions.shape[2]
    )

    # return (
    #     num_zen_garnet_distance / numerical_normalization
    #     + num_zen_lud_distance / numerical_normalization
    #     + num_garnet_lud_distance / numerical_normalization
    #     + str_zen_garnet_distance / str_normalization
    #     + str_zen_lud_distance / str_normalization
    #     + str_garnet_lud_distance / str_normalization
    #     + bool_zen_garnet_distance / bool_normalization
    #     + bool_zen_lud_distance / bool_normalization
    #     + bool_garnet_lud_distance / bool_normalization
    # ) / 9

    return (
        f.calculate_harmonic_mean(
            np.array(
                [
                    num_zen_garnet_distance,
                    num_zen_lud_distance,
                    num_garnet_lud_distance,
                ]
            ),
            numerical_normalization,
        )
        + f.calculate_harmonic_mean(
            np.array(
                [
                    str_zen_garnet_distance,
                    str_zen_lud_distance,
                    str_garnet_lud_distance,
                ]
            ),
            str_normalization,
        )
        + f.calculate_harmonic_mean(
            np.array(
                [
                    bool_zen_garnet_distance,
                    bool_zen_lud_distance,
                    bool_garnet_lud_distance,
                ]
            ),
            bool_normalization,
        )
    ) / 3


async def wait_for_point_file(experiment_name: str, timeout: int = 10) -> pathlib.Path | None:
    if c.BASE_PATH is not None:
        point_path: pathlib.Path = pathlib.Path(os.path.join(c.BASE_PATH, 'log', 'point'))
    else:
        point_path: pathlib.Path = pathlib.Path(os.path.join('log', 'point'))

    start_poll = time.time()
    time_str = datetime.now().strftime('%H:%M:%S')

    print(f'looking for {experiment_name} at {time_str}')
    while time.time() - start_poll < timeout:
        point_csv: pathlib.Path | None = next(point_path.glob(f'{experiment_name}*.csv'), None)
        if point_csv is not None:
            return point_csv

        await asyncio.sleep(1)

    time_str = datetime.now().strftime('%H:%M:%S')
    print(f'Failed at {time_str}')
    return None


"""
* TODO: Think about scaling at a later stage
* For now, we will have 3 engines to handle the different matches against the MCTS agents
"""
async def orchestrate_matches(
    mutated_motions: list[pandas.DataFrame],
    no_matches: int,
    experiment_name: str,
    experiment_suffix: str,
    engine_multiplier: int,
    game_duration_sec: int = 60,
    visual: bool = False,
) -> float:
    c.NO_GAMES = no_matches
    c.POLL_INTERVAL_SEC = 0
    c.GAME_DURATION_SEC = game_duration_sec

    experiment_name = f'{experiment_name}_iter_{experiment_suffix}'

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
    character_order_combinations: list[tuple[int, int]] = list(combinations([0, 1, 2], 2))
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

    common_commands = [
        'java',
        '-cp',
        os.pathsep.join(['dare.jar', '.']),
        'Main',
        '--limithp',
        str(c.PLAYER_HP),
        str(c.PLAYER_HP),
        # '-df',
        '-r',
        '1',
        '-f',
        str(c.GAME_DURATION_SEC * 60),
        '--time-stamp',
        c.GAME_TIME,
        *(['--headless-mode'] if not visual else []),
        '--input-sync',
        *(['--lightweight-mode'] if not visual else []),
        '--pyftg-mode',
        '--non-delay',
        '2',
    ]

    # print(f'Java jar command:{" ".join(common_commands)}')

    os.makedirs(os.path.join('log', 'engines'), exist_ok=True)

    characters = [
        character_name  #
        for combination in character_order_combinations
        for character_name in [c.CHARACTER_ORDER_REVERSE[combination[0]], c.CHARACTER_ORDER_REVERSE[combination[1]]]  #
    ]
    characters = np.array(characters).reshape(3, -1)

    agents = np.full(shape=(3, 2), fill_value=c.AgentNames.MCTS_AGENT)

    await f.start_simulators(
        engine_multiplier * 3,
        common_commands,
        characters,
        mutated_motions,
        agents,
        experiment_name,
        # deterministic=deterministic, really dont care
        extra_commands=argument_for_custom_motions,
    )

    f.consolidate_data(experiment_name, log_list=[c.LOGS.POINT])

    # To get the game results, we are going to get the HP differences in each game.
    # The first implementation of this is going to be rather crude.
    # We will assume that:
    #   x % 3 == 0 -> zen vd garnet
    #   x % 3 == 1 -> zen vd lud
    #   x % 3 == 2 -> garnet vd lud

    point_csv: pathlib.Path | None = await wait_for_point_file(experiment_name)
    if point_csv is None:
        raise FileExistsError(f'Glob failed to fined experiment | {point_csv} | in folder')
    if not point_csv.exists():
        raise FileExistsError(f"Point file | {point_csv} | doesn't exist folder")

    point_df: pandas.DataFrame = f.read_match_results(point_csv)
    pairing_index = point_df[[c.PointHeaderNames.INSTANCE]].to_numpy()

    hp_diff_zen_garnet = point_df[pairing_index % 3 == 0][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)
    hp_diff_zen_lud = point_df[pairing_index % 3 == 1][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)
    hp_diff_garnet_lud = point_df[pairing_index % 3 == 2][[c.PointHeaderNames.HP_ONE, c.PointHeaderNames.HP_TWO]].to_numpy().astype(np.int16)

    # Think about this more, if we have z-g and z-l, do we need to add g-z again?
    zen_win_rate = (
        (hp_diff_zen_garnet[:, 0] > hp_diff_zen_garnet[:, 1]).sum()  #
        + (hp_diff_zen_lud[:, 0] > hp_diff_zen_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)
    garnet_win_rate = (
        (hp_diff_zen_garnet[:, 0] < hp_diff_zen_garnet[:, 1]).sum()  #
        + (hp_diff_garnet_lud[:, 0] > hp_diff_garnet_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)
    lud_win_rate = (
        (hp_diff_zen_lud[:, 0] < hp_diff_zen_lud[:, 1]).sum()  #
        + (hp_diff_garnet_lud[:, 0] < hp_diff_garnet_lud[:, 1]).sum()
    ) / (no_matches * engine_multiplier * 2)

    win_rates: np.ndarray = np.array(
        [
            zen_win_rate,
            garnet_win_rate,
            lud_win_rate,
        ]
    )

    win_rates: np.ndarray = f.transform_win_rate_array(win_rates)

    return min(
        f.calculate_harmonic_mean(values=win_rates),
        1,
    )

def gene_to_motions(gene: np.ndarray, motion_coordinates: np.ndarray) -> list[pandas.DataFrame]:
    mutated_motions = [motion.copy() for motion in me.DEFAULT_MOTION_LIST]

    adjustments = gene.reshape(3, -1).copy()

    # TODO: Right now, we are going to use a slow loop version, if you want this to work, we need to ensure that the dtypes we are adjusting are all the same.
    # I.E., numbers, strings, and booleans must be treated differently.

    for index, character_adjustment in enumerate(adjustments):
        rows = motion_coordinates[:, 0]
        cols = motion_coordinates[:, 1]
        for row, col, value in zip(rows, cols, character_adjustment, strict=True):
            mutated_motions[index].iloc[row, col] = value

    return mutated_motions


def get_motion_coordinates(motion_adjustments: dict[str, str]) -> np.ndarray:
    return np.array(
        [
            [
                mn.MotionNames.MOTION_NAMES.index(motion),
                mh.MotionHeaders.HEADERS.index(header),
            ]
            for motion, header in motion_adjustments.items()
        ]
    )