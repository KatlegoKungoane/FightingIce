import os
import pathlib
import pandas

import constants as c
from MotionClasses.MotionHeaders import MotionHeaders as headers


def read_motion_file(motion_path: str) -> pandas.DataFrame:
	print(os.getcwd())
	return pandas.read_csv(
		filepath_or_buffer=motion_path,
		index_col=headers.MOTION_NAME,
		true_values=['TRUE'],
		false_values=['FALSE'],
		dtype=headers.D_TYPE,
	)


def get_motion_difference(motion_original: pandas.DataFrame, motion_custom: pandas.DataFrame) -> pandas.DataFrame:
	return motion_original.compare(motion_custom)


def get_motion_difference_path(motion_original_path: str, motion_custom_path: str) -> pandas.DataFrame:
	motion_original = read_motion_file(motion_original_path)
	motion_custom = read_motion_file(motion_custom_path)

	return get_motion_difference(motion_original, motion_custom)


class MotionEditor:
	def __init__(
		self,
		character_name: str,
		custom_motion_path: str | None = None,
	) -> None:
		self.character_name: str = character_name
		self.custom_motion_path = custom_motion_path

		default_motion_file_path: str = os.path.join(
			c.DEFAULT_MOTIONS_PATH,
			character_name,
			'Motion.csv',
		)
		self.motion_default: pandas.DataFrame = read_motion_file(default_motion_file_path)

		self.motion_custom: pandas.DataFrame = (
			read_motion_file(custom_motion_path)  #
			if custom_motion_path is not None and os.path.exists(custom_motion_path)
			else read_motion_file(default_motion_file_path)
		)

	def save_custom_motion(self, path: str | None = None) -> None:
		motion_custom_copy = self.motion_custom.copy()

		motion_custom_copy[headers.ATTACK_DOWN_PROP] = motion_custom_copy[headers.ATTACK_DOWN_PROP].map({True: 'TRUE', False: 'FALSE'})
		motion_custom_copy[headers.CONTROL] = motion_custom_copy[headers.CONTROL].map({True: 'TRUE', False: 'FALSE'})
		motion_custom_copy[headers.LANDING_FLAG] = motion_custom_copy[headers.LANDING_FLAG].map({True: 'TRUE', False: 'FALSE'})

		determined_path = (
			path  #
			if path is not None
			else self.custom_motion_path
		)

		pathlib.Path(determined_path).parent.mkdir(
			parents=True,
			exist_ok=True,
		)

		motion_custom_copy.to_csv(determined_path)
