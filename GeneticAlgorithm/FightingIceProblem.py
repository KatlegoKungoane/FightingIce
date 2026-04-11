from typing import Any
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas
import functions as f
import asyncio
import pathlib
import re
from pymoo.parallelization.dask import DaskParallelization
from pymoo.core.problem import LoopedElementwiseEvaluation
import uuid
from datetime import datetime

import constants as c
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
        experiment_name: str,
        no_matches: int = 1,
        engine_multiplier: int = 1,
        game_duration_sec: int = 60,
        elementwise: bool = True,
        visual: bool = False,
        elementwise_runner: DaskParallelization | None = None,
        **kwargs: Any,
    ) -> None:

        self.visual = visual
        self.experiment_name = experiment_name
        self.no_matches = no_matches
        self.engine_multiplier = engine_multiplier
        self.game_duration_sec = game_duration_sec

        # Going to adjust the experiment name if its already in use
        pathlib.Path(c.CUSTOM_MOTION_PATH).mkdir(parents=True, exist_ok=True)
        experiment_name_regex = re.compile(rf'{experiment_name}_(\d+).*')
        experiment_name_number: int = -1
        for directory in pathlib.Path(c.CUSTOM_MOTION_PATH).iterdir():
            match = experiment_name_regex.match(directory.name)
            if match:
                experiment_name_number = max(-1, int(match.group(1)))

        self.experiment_name = f'{experiment_name}_{experiment_name_number + 1}'
        print(f'Derived experiment name: {self.experiment_name}')

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

        if elementwise_runner is None:
            elementwise_runner = LoopedElementwiseEvaluation()

        super().__init__(
            elementwise,
            **kwargs,
            n_var=gene_count,
            n_obj=2,
            # n_ieq_constr=gene_count,
            n_ieq_constr=0,
            xl=xl,
            xu=xu,
            elementwise_runner=elementwise_runner,
        )

    def _evaluate(
        self,
        x: np.ndarray,
        out: dict[str, np.ndarray],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Get uniqueness reward
        # Get competitive balance reward

        # TODO: FIX ME PROPERLY
        x = x.astype(int)

        mutated_motions = [motion.copy() for motion in motion_editor.DEFAULT_MOTION_LIST]

        adjustments = x.reshape(3, -1).copy()

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

        average_win_rate = asyncio.run(
            gf.orchestrate_matches(
                mutated_motions=mutated_motions,
                no_matches=self.no_matches,
                experiment_name=self.experiment_name,
                # Could use this, but we already include the date in the other indicators, so unnecessary
                # %Y%m%d_%H%M%S
                experiment_suffix=f'{uuid.uuid4().hex[:6]}_{datetime.now().strftime('%H%M%S')}',
                engine_multiplier=self.engine_multiplier,
                game_duration_sec=self.game_duration_sec,
                visual=self.visual,
            )
        )

        competitive_balance: float = f.transform_win_rate(average_win_rate)

        out['F'] = np.array([0, -competitive_balance], dtype=np.float64)
        # out['F'] = np.array([-uniqueness_reward, 0], dtype=np.float64)
        # out['G'] = np.array([uniqueness_reward, competitive_reward], dtype=np.float128)

