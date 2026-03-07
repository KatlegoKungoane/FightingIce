import os

import constants as c
import MotionClasses.MotionEditor as me
from MotionClasses.MotionEditor import MotionEditor
from MotionClasses.MotionHeaders import MotionHeaders as headers
from MotionClasses.MotionNames import MotionNames as motion_names

motion_editor = MotionEditor(
	c.CHARACTERS.ZEN,
	os.path.join(
		'custom_motions',
		'motion_editor_1.csv',
	),
)

print(motion_editor.motion_custom.columns)
motion_editor.motion_custom.at[motion_names.NEUTRAL, headers.FRAME_NUMBER] += 50
motion_editor.save_custom_motion(motion_editor.custom_motion_path)

t = me.get_motion_difference(motion_editor.motion_default, motion_editor.motion_custom)
print('t', t)
