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

import constants as c
import dill

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from GeneticAlgorithm.FightingIceProblem import FightingIceProblem
from pymoo.termination import get_termination

res = minimize(
    problem=FightingIceProblem(
        experiment_name='competitive_tests',
        engine_multiplier=3,
        no_matches=3,
    ),
    algorithm=NSGA2(
        pop_size=30,
    ),
    termination=get_termination(c.pymoo.TERMINATION.EVALUATION_LIMIT, 300),
    seed=1,
    save_history=True,
    verbose=True,
)

with open('res.pkl', 'wb') as res_file:
    dill.dump(res, res_file)