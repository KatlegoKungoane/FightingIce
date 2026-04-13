#!/bin/bash
#SBATCH -p stampede
#SBATCH -c 15
#SBATCH -N 20
#SBATCH -J ga_r
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

conda run -n fightingIceEnv_stable python main.py -p 'stampede' -c 15 -n 20