from typing import Any
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas
import functions as f
import asyncio

from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names
import MotionClasses.MotionEditor as motion_editor
import GeneticAlgorithm.genetic_functions as gf

"""
    * We need to think about if we are going to use Problem or ElementWiseProblem.
    * Right now, I am leaning more towards element wise, and will use something to parallelized the process.

    * Now talking about the data structures.
    * Its going to be a meta state set for all 3 characters...
"""

"""
    We are going to handle the meta variable changes manually in this class...
    Not something that can really be passed you know...

    Right now, we are going to work with:
        * Damage - stand a
        * Hit Add Energy - stand b
"""


class FightingIceProblem(ElementwiseProblem):
    def __init__(
        self,
        elementwise: bool = True,
        **kwargs: Any,
    ) -> None:
        # For the first iteration, we are only going to increase the hit damage for stand a, and energy add for stand b
        # Remember this is for every character
        self.motion_adjustments: dict[str, str] = {
            motion_names.STAND_A: headers.ATTACK_HIT_DAMAGE,
            motion_names.STAND_B: headers.ATTACK_HIT_ADD_ENERGY,
        }

        self.motion_coordinates = np.array(
            [
                [
                    motion_names.MOTION_NAMES.index(motion),
                    headers.HEADERS.index(header),
                ]
                for motion, header in self.motion_adjustments.items()
            ]
        )

        # might not be needed
        self.motion_mapper = f.motion_cord_to_index_bulk(self.motion_coordinates)

        gene_count: int = len(self.motion_adjustments) * 3
        xl = np.zeros(shape=gene_count, dtype=np.int64)
        xu = np.zeros(shape=gene_count, dtype=np.int64)

        for character_index in range(3):
            for index, header in enumerate(self.motion_adjustments.values()):
                xl[character_index * (gene_count // 3) + index] = headers.MOTION_LIMITS[header]['min']
                xu[character_index * (gene_count // 3) + index] = headers.MOTION_LIMITS[header]['max']

        super().__init__(
            elementwise,
            **kwargs,
            n_var=gene_count,
            n_obj=2,
            # n_ieq_constr=gene_count,
            n_ieq_constr=0,
            xl=xl,
            xu=xu,
        )

        self.current_eval: int = 0

    def _evaluate(
        self,
        x: np.ndarray,
        out: dict[str, np.ndarray],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Get uniqueness reward
        # Get competitive balance reward

        x = x.astype(int)

        mutated_motions = [motion.copy() for motion in motion_editor.DEFAULT_MOTION_LIST]
        print(mutated_motions[0].columns)

        adjustments = x.reshape(3, -1).copy()
        print('adjustments', adjustments)

        # TODO: Right now, we are going to use a slow loop version, if you want this to work, we need to ensure that the dtypes we are adjusting are all the same.
        # I.E., numbers, strings, and booleans must be treated differently.

        for index, character_adjustment in enumerate(adjustments):
            rows = self.motion_coordinates[:, 0]
            cols = self.motion_coordinates[:, 1]
            for row, col, value in zip(rows, cols, character_adjustment, strict=True):
                mutated_motions[index].iloc[row, col] = value

            # print(mutated_motions[index].loc[:, [headers.ATTACK_HIT_DAMAGE, headers.ATTACK_HIT_ADD_ENERGY]])
            # selected_motion = mutated_motions[index]
            # rows = self.motion_coordinates[:, 0]
            # cols = self.motion_coordinates[:, 1]
            # selected_motion.values[rows, cols] = character_adjustment
            # print(selected_motion.loc[:, [headers.ATTACK_HIT_DAMAGE, headers.ATTACK_HIT_ADD_ENERGY]])

        # with f.full_view():
        # for mutated_motion in mutated_motions:
        # print(mutated_motion.loc[:, [headers.ATTACK_HIT_DAMAGE, headers.ATTACK_HIT_ADD_ENERGY]])
        # print(mutated_motion)

        # TODO: Normalize uniqueness and competitive balance
        numerical_differences = np.stack([motion.select_dtypes('number') for motion in mutated_motions])
        uniqueness_reward = gf.constraint_novelty_search(
            numerical_differences,
            None,
            None,
        )

        # competitve_reward = gf.competitive_balance(mutated_motions)
        competitive_reward = asyncio.run(
            gf.orchestrate_matches(
                mutated_motions=mutated_motions,
                no_matches=1,
                experiment_name='first_run',
                iteration_count=self.current_eval,
                engine_count=3
            )
        )

        out['F'] = np.array([-uniqueness_reward, -competitive_reward], dtype=np.float64)
        # out['G'] = np.array([uniqueness_reward, competitive_reward], dtype=np.float128)

        self.current_eval += 1
