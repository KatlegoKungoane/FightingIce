import asyncio
import numpy as np
import os

from pyftg.socket.aio.gateway import Gateway
import MotionClasses.MotionEditor as me
from MotionClasses.MotionNames import MotionNames as motion_names
from MotionClasses.MotionHeaders import MotionHeaders as headers
import GeneticAlgorithm.genetic_functions as gf
import pathlib
import pandas

import constants as c
import functions as f
from itertools import combinations

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

import GeneticAlgorithm.FightingIceProblem as fp
import sys

gene = np.array(
    [
        193,
        225,
        137,
        66,
        103,
        43,
        20,
        66,
        214,
        219,
        289,
        97,
        43,
        131,
        99,
        181,
        30,
        278,
        19,
        118,
        117,
        51,
        250,
        293,
        176,
        49,
        86,
        137,
        126,
        146,
        188,
        93,
        126,
        82,
        171,
        161,
        21,
        118,
        33,
        86,
        14,
        170,
        226,
        176,
        10,
        296,
        182,
        103,
        295,
        50,
        255,
        271,
        167,
        178,
        169,
        289,
        60,
        117,
        9,
        15,
        292,
        50,
        212,
        165,
        4,
        173,
        254,
        113,
        287,
        250,
        135,
        276,
        108,
        230,
        125,
        144,
        172,
        195,
        158,
        78,
        270,
        10,
        96,
        133,
        277,
        133,
        81,
        276,
        296,
        25,
    ]
)

motion_adjustments: list[tuple[str, str]] = [
    (motion_names.STAND_A, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.STAND_A, headers.ATTACK_GIVE_ENERGY),
    (motion_names.STAND_B, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.STAND_B, headers.ATTACK_GIVE_ENERGY),
    (motion_names.CROUCH_A, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.CROUCH_A, headers.ATTACK_GIVE_ENERGY),
    (motion_names.CROUCH_B, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.CROUCH_B, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_A, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_A, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_B, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_B, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_DA, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_DA, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_DB, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_DB, headers.ATTACK_GIVE_ENERGY),
    (motion_names.STAND_FA, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.STAND_FA, headers.ATTACK_GIVE_ENERGY),
    (motion_names.STAND_FB, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.STAND_FB, headers.ATTACK_GIVE_ENERGY),
    (motion_names.CROUCH_FA, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.CROUCH_FA, headers.ATTACK_GIVE_ENERGY),
    (motion_names.CROUCH_FB, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.CROUCH_FB, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_FA, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_FA, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_FB, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_FB, headers.ATTACK_GIVE_ENERGY),
    (motion_names.AIR_UA, headers.ATTACK_HIT_ADD_ENERGY),
    (motion_names.AIR_UA, headers.ATTACK_GIVE_ENERGY),
]

motion_coordinates: np.ndarray = gf.get_motion_coordinates(motion_adjustments)
numerical_mapped_motion_coordinates = gf.map_numerical_motion_coordinates(motion_adjustments)

experiment_name: str = f.append_time_uuid_experiment('runner_kayyyy')

setting = fp.IndividualSettings(
    motion_coordinates=motion_coordinates,
    mapped_numerical_motion_coordinates=numerical_mapped_motion_coordinates,
    no_matches=8,
    engine_multiplier=4,
    game_duration_sec=c.GAME_DURATION_SEC,
    visual=False,
    experiment_name=f'{experiment_name}{69}',
)
fitness: np.ndarray = fp.evaluate_individual(gene, setting)
print(fitness)

f.consolidate_data(
    experiment_name,
    exclude_list=[
        c.LOGS.POINT,
        c.LOGS.FRAME_DATA,
    ],
)

