import asyncio

import numpy as np

import functions as f
from GeneticAlgorithm.genetic_functions import gene_to_motions, orchestrate_matches
from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names

if __name__ == '__main__':
    motion_adjustments: dict[str, str] = {
        motion_names.STAND_A: headers.ATTACK_HIT_DAMAGE,
        motion_names.STAND_B: headers.ATTACK_HIT_ADD_ENERGY,
    }

    motion_coordinates = np.array(
        [
            [
                motion_names.MOTION_NAMES.index(motion),
                headers.HEADERS.index(header),
            ]
            for motion, header in motion_adjustments.items()
        ]
    )
    gene: np.ndarray = np.array([272, 212, 191, 60, 309, 54], dtype=int)

    mutated_motions = gene_to_motions(gene, motion_coordinates)

    average_win_rate = asyncio.run(
        orchestrate_matches(
            mutated_motions=mutated_motions,
            no_matches=1,
            experiment_name='visual',
            experiment_suffix='',
            engine_multiplier=6,
            game_duration_sec=60,
            visual=False,
        )
    )

    competitive_balance: float = f.transform_win_rate(average_win_rate)

    print(f"Balance reward: {competitive_balance}")