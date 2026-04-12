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

if __name__ == '__main__':
    scheduler_address = os.environ.get('DASK_SCHEDULER_ADDRESS')
    client = (
        Client(scheduler_address)  #
        if scheduler_address
        else Client(
            n_workers=2,
            threads_per_worker=7,
            # To match cores with cluster count
            resources={'cores': 15},
        )
    )

    print(f'Dask Dashboard available at: {client.dashboard_link}')

    try:
        # runner = DaskParallelization(client)

        problem = FightingIceProblem(
            experiment_name='dask_tests',
            dask_client=client,
            engine_multiplier=2,
            no_matches=1,
            game_duration_sec=60,
            visual=False,
            # elementwise_runner=runner,
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
                    n_partitions=4,
                ),
                # Magic number is 20
                n_neighbors=3,
                decomposition=PBI(),
                sampling=IntegerRandomSampling(),
                crossover=SBX(prob=1.0, eta=20, vtype=int),
                mutation=PolynomialMutation(prob=1.0, eta=20, vtype=int),
            ),
            termination=get_termination(c.pymoo.TERMINATION.GENERATION_LIMIT, 3),
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
        client.close()
