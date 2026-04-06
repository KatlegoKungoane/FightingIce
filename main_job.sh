#!/bin/bash
#SBATCH -p bigbatch
#SBATCH -c 16
#SBATCH -J ga_r
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

conda run -n fightingIceEnv_stable python main.py