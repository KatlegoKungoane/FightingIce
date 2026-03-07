import argparse
import asyncio
import datetime
import os
import pathlib
import re
import shutil
import socket
import subprocess
import time

import aiofiles
import numpy as np
from pyftg.socket.aio.gateway import Gateway

import constants as c
from agents.KatKickAi import KatKickAi
from MotionClasses.MotionEditor import MotionEditor

def arg_parser() -> str:
	parser: argparse.ArgumentParser = argparse.ArgumentParser(description='FightingICE Research Runner')

	parser.add_argument(
		'-hp',
		'--player_hit_points',
		type=int,
		default=-1,
		help='Hit-points for both agents',
	)
	parser.add_argument(
		'-i',
		'--poll_interval_sec',
		type=int,
		default=-1,
		help='Time lag for updating console log',
	)
	parser.add_argument(
		'-e',
		'--engine_count',
		type=int,
		default=-1,
		help='Number of engines that will run at once',
	)
	parser.add_argument(
		'-g',
		'--no_games',
		type=int,
		default=-1,
		help='Number of games each engine will simulate',
	)
	parser.add_argument(
		'-d',
		'--game_duration',
		type=int,
		default=-1,
		help='Max drain of each match between agents',
	)
	parser.add_argument(
		'-exp',
		'--game_name',
		type=str,
		default='adhoc',
		help='Name of the experiment',
	)
	parser.add_argument(
		'-zip',
		'--zip_files',
		type=str,
		default='True',
		help='Flag to ascertain if log files should be zipped or not',
	)

	# Booleans (Flags)
	# action="store_true" means if the flag is present, it's True. If not, it's False.
	# parser.add_argument("--headless", action="store_true", help="Run in headless mode")

	args = parser.parse_args()

	c.NO_ENGINES = (
		c.NO_ENGINES  #
		if args.engine_count == -1
		else args.engine_count
	)
	c.NO_GAMES = (
		c.NO_GAMES  #
		if args.no_games == -1
		else args.no_games
	)
	c.PLAYER_HP = (
		c.PLAYER_HP  #
		if args.player_hit_points == -1
		else args.player_hit_points
	)
	c.POLL_INTERVAL_SEC = (
		c.POLL_INTERVAL_SEC  #
		if args.poll_interval_sec == -1
		else args.poll_interval_sec
	)
	c.GAME_DURATION_SEC = (
		c.GAME_DURATION_SEC  #
		if args.game_duration == -1
		else args.game_duration
	)
	c.EXPERIMENT_NAME = (
		c.EXPERIMENT_NAME  #
		if args.game_name == 'adhoc'
		else args.game_name
	)
	c.ZIP_FILES = (
		c.ZIP_FILES  #
		if args.zip_files == 'True'
		else False
	)

	return args.game_name


"""
	We currently have so many logs in the root folders.
	We need to consolidate everything into a single file, and maybe format it as well
"""


def get_number_from_file_name(file_name: str, string_to_find: str) -> int:
	match = re.search(rf'{string_to_find}-(\d+)', file_name)

	if match:
		return int(match.group(1))
	return -1


def consolidate_data(experiment_name: str) -> None:
	# We will first throw an error if you add a folder to the logs that we are not aware of
	directory: pathlib.Path = pathlib.Path('log')
	unknown_directories: list[str] = []

	for folder in directory.iterdir():
		if folder.is_dir() and folder.name not in c.KNOWN_LOGS:
			unknown_directories.append(folder.name)

	if len(unknown_directories) != 0:
		raise FileNotFoundError(
			'Known log directories are:',  #
			','.join(c.KNOWN_LOGS),
			'\nFound these unknown directories:',
			','.join(unknown_directories),
		)

	for log_group_name in c.KNOWN_LOGS:
		log_group: pathlib.Path = directory.joinpath(log_group_name)
		# We will first check if it is already in a folder

		time_stamps: set = set()
		file_names: list[str] = []
		for file in log_group.iterdir():
			if file.is_file():
				file_names.append(file.name)
				time_stamps.add(file.name.split('-').pop().rsplit('.', 1)[0])

		for time_stamp in time_stamps:
			experiment_regex: re.Pattern = re.compile(rf'{re.escape(experiment_name)}.*?{re.escape(time_stamp)}')

			experiment_files: list[pathlib.Path] = []
			for experiment in file_names:
				if experiment_regex.match(experiment):
					experiment_files.append(directory.joinpath(log_group_name, experiment))

			file_extension = file_names[0].split('.')[-1]
			consolidated_file_name: pathlib.Path = directory.joinpath(log_group_name, f'{experiment_name}-{time_stamp}.{file_extension}')

			if len(experiment_files) == 0:
				continue

			if log_group_name == 'replay':
				experiment_folder_name: str = f'{experiment_name}-{c.GAME_TIME}'
				log_group_path: str = os.path.join('log', log_group_name)
				experiment_folder_path: str = os.path.join(log_group_path, experiment_folder_name)
				os.makedirs(experiment_folder_path, exist_ok=True)
				for experiment_file in experiment_files:
					experiment_file.rename(
						os.path.join(
							'log',
							log_group_name,
							experiment_folder_name,
							experiment_file.name,
						)
					)

				if c.ZIP_FILES:
					experiment_folder = os.path.join(log_group_path, experiment_folder_name)
					shutil.make_archive(
						experiment_folder,
						'zip',
						experiment_folder_path,
					)

					purge_directory(experiment_folder, True)
			else:
				"""
					we will handle the points and the frame data differently.
				"""
				with consolidated_file_name.open(mode='w') as consolidated_file:
					if log_group_name == 'frameData':
						consolidated_file.write('[')

					for experiment_file in experiment_files:
						if experiment_file.name == consolidated_file_name.name:
							continue

						if log_group_name == 'frameData':
							consolidated_file.write(f'{{"{experiment_file.name}":')
						elif log_group_name != 'point':
							consolidated_file.write(f'{experiment_file}\n')

						with experiment_file.open(mode='r') as src_file:
							if log_group_name == 'point':
								instance_number: int = get_number_from_file_name(experiment_file.name, 'instance')
								round_number: int = get_number_from_file_name(experiment_file.name, 'round')
								match_result: list[str] = src_file.readline().split(',')
								# Remove the round count from the engine
								match_result.pop(0)
								match_result.pop()
								winner: int = (match_result[0] > match_result[1]) - (match_result[1] > match_result[0])
								consolidated_file.write(f'{instance_number},{round_number},{",".join(match_result)},{winner}')
							else:
								shutil.copyfileobj(src_file, consolidated_file)

						if log_group_name == 'frameData':
							consolidated_file.write('},\n')
						else:
							consolidated_file.write('\n')

						experiment_file.unlink(missing_ok=True)

					if log_group_name == 'frameData':
						consolidated_file.write(']')


def create_gateways(start_port: int, end_port: int, limit: int = 100) -> list[Gateway]:
	gateways: list[Gateway] = []

	for port in range(start_port, end_port + 1):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			try:
				s.bind(('127.0.0.1', port))
				gateways.append(Gateway(port=port))
			except OSError:
				continue

		if len(gateways) >= limit:
			break

	return gateways


def kill_process(process: asyncio.subprocess.Process) -> None:
	if process.returncode is None:
		print(f'Forcefully killing process tree for PID {process.pid}...')

		# Windows
		if os.name == 'nt':
			subprocess.run(
				['taskkill', '/F', '/T', '/PID', str(process.pid)],
				capture_output=True,
				check=True,
			)
		# Linux/Mac
		else:
			process.kill()


async def close_files(log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper]) -> None:
	for file in log_files:
		await file.close()


def kill_processes(
	simulators: list[asyncio.subprocess.Process],  #
	experiment_name: str,
	consolidate_input: bool = True,
) -> None:
	for simulator in simulators:
		kill_process(simulator)

	if consolidate_input:
		consolidate_data(experiment_name)


async def process_simulator_logs(
	subprocess: list[asyncio.subprocess.Process],
	log_file: aiofiles.threadpool.text.AsyncTextIOWrapper,
	port: int,
	ready_event: asyncio.Event,
) -> None:
	while True:
		line_bytes = await subprocess.stdout.readline()
		if not line_bytes:
			break

		line: str = line_bytes.decode().strip()
		await log_file.write(line + '\n')
		await log_file.flush()

		if 'Waiting to launch a game' in line:
			ready_event.set()

		if any(err in line for err in ['Exception', 'Error', 'SEVERE']):
			print(f'!!! CRITICAL ERROR ON PORT {port} !!!\n{line}')
			kill_process(subprocess)
			break


async def monitor_matches(
	gateways: list[Gateway],  #
	simulators: list[asyncio.subprocess.Process],
	matches: list[asyncio.Task],
) -> None:
	last_heartbeat: float = time.time() + c.POLL_INTERVAL_SEC
	while True:
		active_simulators: np.ndarray = np.full(
			shape=len(gateways),
			fill_value=False,
			dtype=bool,
		)

		for index, (simulator, match) in enumerate(zip(simulators, matches, strict=True)):
			active_simulators[index] = simulator.returncode is None and not match.done()

		if not np.any(active_simulators):
			print('Simulation Completed Successfully (Maybe)')
			break

		if time.time() - last_heartbeat >= c.POLL_INTERVAL_SEC:
			last_heartbeat: float = time.time()
			print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			line: str = ''
			for index, is_active in enumerate(active_simulators):
				line += f'Port: {gateways[index].port} - {"ACTIVE" if is_active else "DEAD  "}'
			print(line)
			for match in matches:
				print(f'Match {"playing" if not match.done() else "finished"}')
				print(match._state)
			# print(f"\033[{len(active_simulators) + 2}F", end="", flush=True)
			# print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "\n")
			# line = ""
			# for index, is_active in enumerate(active_simulators):
			#     line += f"Port: {gateways[index].port} - {"ACTIVE" if is_active else "DEAD  "}\n"
			# print(line, end="")
			# print(f"\033[{len(active_simulators) + 2}F", end="", flush=True)

		await asyncio.sleep(1)

	print('All executions are closed')
	for simulator, gateway in zip(simulators, gateways, strict=True):
		print(f'Port: {gateway.port} - {simulator.returncode}')


async def orchestrate_matches(
	gateways: list[Gateway],  #
	simulators: list[asyncio.subprocess.Process],
	simulator_ready_events: list[asyncio.Event],
	log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper],
	characters: list[str],
	motions: list[MotionEditor],
	experiment_name: str,
) -> None:
	matches: list[asyncio.Task] = []

	try:
		print('Waiting for all engines to be ready')
		await asyncio.wait_for(
			asyncio.gather(*(event.wait() for event in simulator_ready_events)),
			timeout=30.0,
		)
		print('All engines are ready')
	except asyncio.TimeoutError:
		print('One or more engines failed to start in time!')
		await close_files(log_files)
		
		kill_processes(
			simulators,
			experiment_name,
		)

	for index, gateway in enumerate(gateways):
		agent1 = KatKickAi(
			use_kick=True,
			interval=0.1,
			character_name=characters[0],
			motion=motions[0],
		)
		agent2 = KatKickAi(
			use_kick=True,
			interval=0.1,
			character_name=characters[1],
			motion=motions[0],
		)

		gateway.register_ai(agent1.name(), agent1)
		gateway.register_ai(agent2.name(), agent2)
		game_name = f'{experiment_name}-instance-{index}-{agent1.name()}-vs-{agent2.name()}'

		matches.append(
			asyncio.create_task(
				gateway.run_game(
					[f'{game_name}<name>{characters[0]}', characters[1]],
					[agent1.name(), agent2.name()],
					c.NO_GAMES,
				)
			)
		)

	# Kill matches if games take too long to finish
	duration: float = c.GAME_DURATION_SEC * c.NO_GAMES * 1.5
	try:
		await asyncio.wait_for(
			monitor_matches(gateways, simulators, matches),
			timeout=duration,
		)
	except asyncio.TimeoutError:
		print(f'[CRITICAL] Experiment exceeded time limit: {duration} sec. Shutting down.')
		await close_files(log_files)
		kill_processes(simulators, experiment_name)

	await close_files(log_files)
	kill_processes(simulators, experiment_name)


async def start_simulators(
	gateways: list[Gateway],
	common_commands: list[str],
	characters: list[str],
	motions: list[MotionEditor],
	experiment_name: str,
) -> None:
	simulators: list[asyncio.subprocess.Process] = []
	log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper] = []
	simulator_ready_events: list[asyncio.Event] = [asyncio.Event() for _ in gateways]

	task_containers: list[asyncio.Task] = []
	for index, gateway in enumerate(gateways):
		log_files.append(
			await aiofiles.open(
				f'log/engines/{experiment_name}-instance-{gateway.port}-{c.GAME_TIME}.log',
				'w',
			)
		)

		proc = await asyncio.create_subprocess_exec(
			*common_commands,
			'--port',
			str(gateway.port),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.STDOUT,
		)
		simulators.append(proc)

		task_containers.append(
			asyncio.create_task(
				process_simulator_logs(
					proc,
					log_files[index],
					gateway.port,
					simulator_ready_events[index],
				)
			)
		)

		print(f'Engine started (PID: {simulators[index].pid}, PORT: {gateway.port}).')

	await orchestrate_matches(
		gateways,
		simulators,
		simulator_ready_events,
		log_files,
		characters,
		motions,
		experiment_name,
	)


# GPT Function, not important to know how to delete files in folder
def purge_directory(target_dir: str | pathlib.Path, remove_root: bool = False) -> None:
	root = pathlib.Path(target_dir)

	if not root.exists():
		print(f'Path {root} does not exist.')
		print(os.getcwd())
		return

	# rglob("*") finds everything recursively
	# We sort them by length descending to ensure we process
	# the deepest files/folders first (children before parents)
	for path in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
		if path.is_file() or path.is_symlink():
			path.unlink()
		elif path.is_dir():
			path.rmdir()

	if remove_root:
		root.rmdir()
