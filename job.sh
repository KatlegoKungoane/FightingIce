#!/bin/bash
#SBATCH -p bigbatch
#SBATCH -c 16
#SBATCH -J rand
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

conda run -n fightingIceEnv_stable python runner.py --game_name "cluster" --player_hit_points 400 --poll_interval_sec 1 --engine_count 1 --no_games 1 --game_duration 60