#!/bin/bash
#SBATCH -p stampede
#SBATCH -c 15
#SBATCH -N 5
#SBATCH -J ga_r
#SBATCH --ntasks-per-node=1
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

NODES=5
CORES=15
DASK_FILE="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce/dask_schedulers/dask_${SLURM_JOB_ID}.json"

conda run -n fightingIceEnv_stable dask-scheduler --scheduler-file $DASK_FILE &
echo "Waiting for scheduler to write $DASK_FILE..."
until [ -f "$DASK_FILE" ]; do
     sleep 0.5
done
echo "Scheduler is online."

srun conda run -n fightingIceEnv_stable dask-worker \
    --scheduler-file $DASK_FILE \
    --nthreads $CORES \
    --resources "cores=$CORES" &

conda run -n fightingIceEnv_stable python main.py -sf $DASK_FILE -n $NODES -c $CORES