import pathlib

import constants as c
import functions as f

for log_group_name in c.KNOWN_LOGS:
    print(f'Clearing files in log/{log_group_name}')
    f.purge_directory(
        str(pathlib.Path('log').joinpath(log_group_name)),
        False,
    )
    print('done\n')
