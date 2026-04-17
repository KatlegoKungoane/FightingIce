# import os

# import constants as c
# import MotionClasses.MotionEditor as me
# from MotionClasses.MotionEditor import MotionEditor
# from MotionClasses.MotionHeaders import MotionHeaders as headers
# from MotionClasses.MotionNames import MotionNames as motion_names

# motion_editor = MotionEditor(
#     c.CHARACTERS.ZEN,
#     os.path.join(
#         'custom_motions',
#         'motion_editor_1.csv',
#     ),
# )

# print(motion_editor.motion_custom.columns)
# motion_editor.motion_custom.at[motion_names.NEUTRAL, headers.FRAME_NUMBER] += 50
# motion_editor.save_custom_motion(motion_editor.custom_motion_path)

# t = me.get_motion_difference(motion_editor.motion_default, motion_editor.motion_custom)
# print('t', t)

# Experiment to determine the point at which running more engines is bad for the system and should rather run more rounds
import constants as c
import functions as f
import dill
import asyncio
import time
import os
import numpy as np
from distributed import Client, LocalCluster
import sys
from dask_jobqueue import SLURMCluster

import MotionClasses.MotionEditor as me
from pymoo.algorithms.moo.moead import MOEAD
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from GeneticAlgorithm.FightingIceProblem import FightingIceProblem
from pymoo.termination import get_termination
from pymoo.util.ref_dirs import get_reference_directions
from pymoo.decomposition.pbi import PBI
from pymoo.parallelization.dask import DaskParallelization
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PolynomialMutation


# async def run_games(no_engines: int):
#     common_commands = [
#         'java',
#         '-cp',
#         os.pathsep.join(['dare.jar', '.']),
#         'Main',
#         '--limithp',
#         str(c.PLAYER_HP),
#         str(c.PLAYER_HP),
#         # '-df',
#         '-r',
#         '1',
#         '-f',
#         str(c.GAME_DURATION_SEC * 60),
#         '--time-stamp',
#         c.GAME_TIME,
#         # '--headless-mode',
#         '--input-sync',
#         # '--lightweight-mode',
#         '--pyftg-mode',
#         '--non-delay',
#         '2',
#     ]
#     await f.start_simulators(
#         no_engines=no_engines,
#         common_commands=common_commands,
#         characters=np.array(
#             [
#                 [c.CHARACTERS.ZEN.name, c.CHARACTERS.GARNET.name],
#                 [c.CHARACTERS.ZEN.name, c.CHARACTERS.LUD.name],
#                 [c.CHARACTERS.GARNET.name, c.CHARACTERS.LUD.name],
#             ]
#         ),
#         # Not really used anyways
#         motions=me.DEFAULT_MOTION_LIST,
#         agent_names=np.full(shape=(3, 2), dtype=object, fill_value=c.AgentNames.MCTS_AGENT),
#         experiment_name='low',
#         deterministic=True,
#     )


# if __name__ == '__main__':
#     c.start_time = time.perf_counter()
#     # c.PLAYER_HP = 10000
#     c.NO_GAMES = 2
#     c.POLL_INTERVAL_SEC = 0
#     asyncio.run(run_games(no_engines=1))
#     print(f'time: {c.end_time - c.start_time}')


# Clock time experiments
# MOEAD - pop = 3 - time = 222.09393120001187
# NSGA - pop = 3 - time = 236.92388630000642

# Uniqueness adjustments tests
# import GeneticAlgorithm.genetic_functions as gf

# from MotionClasses.MotionHeaders import MotionHeaders as headers
# from MotionClasses.MotionNames import MotionNames as motion_names

# if __name__ == '__main__' and False:
#     motion_adjustments: list[tuple[str, str]] = [
#         (motion_names.STAND_A, headers.ATTACK_HIT_ADD_ENERGY),
#         (motion_names.STAND_A, headers.ATTACK_GIVE_ENERGY),
#     ]

#     motion_coordinates = gf.get_motion_coordinates(motion_adjustments)
#     x = gf.generate_random_gene(motion_adjustments)
#     mutated_motions = gf.gene_to_motions(gene=x, motion_coordinates=motion_coordinates)
#     mapped_motion_coordinates = gf.map_numerical_motion_coordinates(motion_adjustments)

#     numerical_differences = np.stack([motion.select_dtypes('number') for motion in mutated_motions])
#     uniqueness_reward = gf.constraint_novelty_search(
#         numerical_motions=numerical_differences,
#         motion_coordinates=motion_coordinates,
#         mapped_numerical_motion_coordinates=mapped_motion_coordinates,
#         string_motions=None,
#         boolean_motions=None,
#     )

if __name__ == '__main__':
    f.arg_parser()

    if c.SCHEDULER_FILE is not None:
        print("--- Running with Scheduler File ---")
        client = Client(scheduler_file=c.SCHEDULER_FILE)

        print(f"Waiting for workers to report for duty...")
        client.wait_for_workers(n_workers=c.NODES, timeout=30)
        print("Cluster is fully populated. Starting Evolution.")
    else:
        print("--- Running with LocalCluster ---")

        core_count: int = c.CORES // c.NODES
        cluster = LocalCluster(
            n_workers=c.NODES,
            threads_per_worker=core_count,
            resources={'cores': core_count}
        )

        client = Client(cluster)

    print(f'Dask Dashboard available at: {client.dashboard_link}')

    try:
        problem = FightingIceProblem(
            experiment_name='mixed_exp_02_32v',
            dask_client=client,
            engine_multiplier=4,
            no_matches=10,
            game_duration_sec=60,
            visual=False,
        )

        start_time = time.perf_counter()
        res = minimize(
            problem=problem,
            algorithm=MOEAD(
                # N = n_partitions + 1 (for n_obj == 2)
                # Must be greater than n_neighbors
                ref_dirs=get_reference_directions(
                    c.pymoo.MOEAD.SpreadType.DAS_DENNIS,
                    n_dim=2,
                    n_partitions=39,
                ),
                # Magic number is 20
                n_neighbors=20,
                decomposition=PBI(),
                sampling=IntegerRandomSampling(),
                crossover=SBX(prob=1.0, eta=20, vtype=int),
                mutation=PolynomialMutation(prob=1.0, eta=20, vtype=int),
            ),
            termination=get_termination(c.pymoo.TERMINATION.GENERATION_LIMIT, 10),
            seed=1,
            save_history=True,
            verbose=True,
        )

        f.consolidate_data(
            problem.experiment_name,
            exclude_list=[c.LOGS.POINT],
        )

        end_time = time.perf_counter()
        print(f'time: {end_time - start_time}')

        with open('res.pkl', 'wb') as res_file:
            dill.dump(res, res_file)
    finally:
        client.shutdown()
        client.close()
