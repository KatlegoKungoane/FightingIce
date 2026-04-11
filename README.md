# TODO List
- Look into method for keeping all engines alive and retroactively setting the meta state values. We spend a lot of time in startups of the engines.
- Look into running games on demand. We currently wait for all to finish before starting / ending other games. We can speed that up maybe...
- Validate that the correct motions are assigned to the correct character pair!
- Further refine meta state ranges
- Add constraints for the meta state (G)
- Logging: Ensure log/engines/ is on the cluster's high-speed "scratch" storage, or the I/O might slow down your simulation.
- Correct the uniqueness constraint... Its looking at everything, which isnt fair. We need louder signals for things we actually control.

# Note list
- N in MOEA is calculated as:
$$N = \binom{H + m - 1}{m - 1}$$
- Where H is n_partitions
- When running the code in a conda environment, you need to execute: conda install -c conda-forge openjdk=21.0.2. Need to figure out way to include this such that ita easy to start up
- We got 20 cores on my BBD laptop (might change when I move jobs)
- The harmonic mean calculation is:
$$\frac{n}{x_1^{-1}+\dots+x_n^{-1}} \quad s.t: 0\leq x_i \leq 1$$