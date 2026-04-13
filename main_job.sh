#!/bin/bash
#SBATCH -p stampede
#SBATCH -c 15
#SBATCH -N 3
#SBATCH -J ga_r
#SBATCH --ntasks-per-node=1
#SBATCH -o /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/out/slurm.%N.%j.out
#SBATCH -e /home-mscluster/kkungoane/dare-fighting-ice/FightingIce/err/slurm.%N.%j.err

mkdir -p dask_logs

PROJECT_ROOT="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce"
export PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

NODES=3
CORES=15
DASK_FILE="/home-mscluster/kkungoane/dare-fighting-ice/FightingIce/dask_schedulers/dask_${SLURM_JOB_ID}.json"

conda run -n fightingIceEnv_stable dask scheduler \
        --scheduler-file $DASK_FILE \
        --port 0 \
        > dask_logs/scheduler_$SLURM_JOBIID 2>&1 &
echo "Waiting for scheduler to write $DASK_FILE..."
until [ -f "$DASK_FILE" ]; do
     sleep 0.5
done
echo "Scheduler is online."

# We set quiet to silence the valid termination of srun
srun --quiet conda run -n fightingIceEnv_stable dask-worker \
    --scheduler-file $DASK_FILE \
    --nthreads $CORES \
    --resources "cores=$CORES" \
    > dask_logs/worker_$SLURM_JOB_ID 2>&1 &

conda run -n fightingIceEnv_stable python main.py -sf $DASK_FILE -n $NODES -c $CORES