import argparse
import asyncio
import datetime
import os
import socket
import subprocess
import time

import numpy as np
from pyftg.socket.aio.gateway import Gateway

import constants as c
from agents.DisplayInfo import DisplayInfo
from agents.KickAI import KickAI

"""
    TODO: 
        * Investigate why we are still using that hpmode stuff in other logs
        * Write all logs into respective experiment folder name
        * Get the overwriting thing working well.
        * Linter
"""

# We are going to get a list of available ports. Then start according to the args passed in


def arg_parser():
	parser = argparse.ArgumentParser(description='FightingICE Research Runner')

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

	# Booleans (Flags)
	# action="store_true" means if the flag is present, it's True. If not, it's False.
	# parser.add_argument("--headless", action="store_true", help="Run in headless mode")

	args = parser.parse_args()

	c.NO_ENGINES = c.NO_ENGINES if args.engine_count == -1 else args.engine_count
	c.NO_GAMES = c.NO_GAMES if args.no_games == -1 else args.no_games
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


arg_parser()

common_commands = [
	'java',
	'-cp',
	os.pathsep.join(['dare.jar', '.']),
	'Main',
	'--limithp',
	str(c.PLAYER_HP),
	str(c.PLAYER_HP),
	'-df',
	'-r',
	'1',
	'-f',
	str(c.GAME_DURATION_SEC * 60),
	# '--config-path',
	# '1',
	# 'zen',
	# './custom_motions/zen.csv',
	# This is for the ai, so maybe turn on when you have those configured
	'--headless-mode',
	'--input-sync',
	# Investigate this mode
	'--lightweight-mode',
	'--pyftg-mode',
	'--non-delay',
	'2',
]

print(' '.join(common_commands))


def create_gateways(start_port, end_port, limit=100):
	gateways = []

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


available_gateways = create_gateways(8000, 9000, limit=c.NO_ENGINES)

subprocesses = []
log_files = []
os.makedirs(f'log/engines/{c.EXPERIMENT_NAME}', exist_ok=True)


def kill_process(proc):
	# if proc.poll() is None:
	if proc.returncode is None:
		print(f'Forcefully killing process tree for PID {proc.pid}...')

		# Windows
		if os.name == 'nt':
			subprocess.run(
				['taskkill', '/F', '/T', '/PID', str(proc.pid)], capture_output=True
			)
		# Linux/Mac
		else:
			proc.kill()

		# proc.wait()


def kill_processes():
	for proc in subprocesses:
		kill_process(proc)


async def log_monitor(subprocess, log_file, port):
	while True:
		line_bytes = await subprocess.stdout.readline()
		if not line_bytes:
			break

		line = line_bytes.decode().strip()
		log_file.write(line + '\n')
		log_file.flush()

		if any(err in line for err in ['Exception', 'Error', 'SEVERE']):
			print(f'!!! CRITICAL ERROR ON PORT {port} !!!\n{line}')
			kill_process(subprocess)
			break


matches = []
monitor_logs = []


async def start_matches():
	for index, port in enumerate(gateway.port for gateway in available_gateways):
		log_files.append(
			open(
				f'log/engines/{c.EXPERIMENT_NAME}/instance-{port}-{datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")}.log',
				'w',
			)
		)
		proc = await asyncio.create_subprocess_exec(
			*common_commands,
			'--port',
			str(port),
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.STDOUT,
		)
		subprocesses.append(proc)

		# Start a dedicated logger task for THIS specific engine immediately
		monitor_logs.append(
			asyncio.create_task(log_monitor(proc, log_files[index], port))
		)

		print(f'Engine started (PID: {subprocesses[index].pid}, PORT: {port}).')

	await asyncio.sleep(3)
	for index, gateway in enumerate(available_gateways):
		agent1 = KickAI()
		agent2 = DisplayInfo()
		gateway = available_gateways[index]
		gateway.register_ai('KickAI', agent1)
		gateway.register_ai('DisplayInfo', agent2)
		game_name = (
			f'{c.EXPERIMENT_NAME}-instance-{index}-{agent1.name()}-vs-{agent2.name()}'
		)

		task = asyncio.create_task(
			gateway.run_game(
				[f'{game_name}<name>ZEN', 'ZEN'], ['KickAI', 'DisplayInfo'], c.NO_GAMES
			)
		)
		matches.append(task)

	# monitor_logs.append(
	# 	asyncio.create_task(log_monitor(subprocesses, log_files, available_gateways))
	# )

	async def monitor():
		last_heartbeat = time.time() + c.POLL_INTERVAL_SEC
		while True:
			active_processes = np.full(
				shape=(len(available_gateways)), fill_value=False, dtype=bool
			)
			for index, (subprocess, match) in enumerate(zip(subprocesses, matches)):
				active_processes[index] = (
					subprocess.returncode is None and not match.done()
				)

			# All are dead
			if not np.any(active_processes == True):
				break

			if time.time() - last_heartbeat >= c.POLL_INTERVAL_SEC:
				last_heartbeat = time.time()
				print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				line = ''
				for index, is_active in enumerate(active_processes):
					line += f'Port: {available_gateways[index].port} - {"ACTIVE" if is_active else "DEAD  "}'
				print(line)
				for match in matches:
					print(f'Match {"playing" if not match.done() else "finished"}')
					print(match._state)
				# print(f"\033[{len(active_processes) + 2}F", end="", flush=True)
				# print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "\n")
				# line = ""
				# for index, is_active in enumerate(active_processes):
				#     line += f"Port: {available_gateways[index].port} - {"ACTIVE" if is_active else "DEAD  "}\n"
				# print(line, end="")
				# print(f"\033[{len(active_processes) + 2}F", end="", flush=True)

			await asyncio.sleep(1)

		print('All executions are closed')
		for index, subprocess in enumerate(subprocesses):
			print(f'Port: {available_gateways[index].port} - {subprocess.returncode}')

	duration = (c.GAME_DURATION_SEC + 4) * 5 * c.NO_GAMES
	try:
		await asyncio.wait_for(monitor(), timeout=duration)
	except asyncio.TimeoutError:
		print(
			f'[CRITICAL] Experiment exceeded time limit: {duration} sec. Shutting down.'
		)
		kill_processes()


asyncio.run(start_matches())
kill_processes()
