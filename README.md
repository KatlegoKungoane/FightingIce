# TODO List
- Currently, my engine multiplier code is really just to get a better average for 1 iteration... we still need to look into doing multiple at once
- Look into method for keeping all engines alive and retroactively setting the meta state values. We spend a lot of time in startups of the engines.
- Look into running games on demand. We currently wait for all to finish before starting / ending other games. We can speed that up maybe...
- Validate that the correct motions are assigned to the correct character pair!
- Further refine meta state ranges
- Add constraints for the meta state (G)


# Note list
- N in MOEA is calculated as:
$$N = \binom{H + m - 1}{m - 1}$$
- Where H is n_partitions