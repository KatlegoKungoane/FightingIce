import argparse
import asyncio
import datetime
import os
import socket
import subprocess
import time

import aiofiles
import numpy as np
from pyftg.socket.aio.gateway import Gateway

import constants as c
from agents.DisplayInfo import DisplayInfo
from agents.KickAI import KickAI


def arg_parser() -> None:
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


def kill_processes(simulators: list[asyncio.subprocess.Process]) -> None:
	for simulator in simulators:
		kill_process(simulator)


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
		kill_processes(simulators)

	for index, gateway in enumerate(gateways):
		agent1 = KickAI()
		agent2 = DisplayInfo()
		gateway.register_ai('KickAI', agent1)
		gateway.register_ai('DisplayInfo', agent2)
		game_name = f'{c.EXPERIMENT_NAME}-instance-{index}-{agent1.name()}-vs-{agent2.name()}'

		matches.append(
			asyncio.create_task(
				gateway.run_game(
					[f'{game_name}<name>ZEN', 'ZEN'],
					['KickAI', 'DisplayInfo'],
					c.NO_GAMES,
				)
			)
		)

	# Kill matches if games take too long to finish
	duration: float = c.GAME_DURATION_SEC * c.NO_GAMES * 5
	try:
		await asyncio.wait_for(
			monitor_matches(gateways, simulators, matches),
			timeout=duration,
		)
	except asyncio.TimeoutError:
		print(f'[CRITICAL] Experiment exceeded time limit: {duration} sec. Shutting down.')
		kill_processes(simulators)

	kill_processes(simulators)


async def start_simulators(
	gateways: list[Gateway],
	common_commands: list[str],
) -> None:
	simulators: list[asyncio.subprocess.Process] = []
	log_files: list[aiofiles.threadpool.text.AsyncTextIOWrapper] = []
	simulator_ready_events: list[asyncio.Event] = [asyncio.Event() for _ in gateways]

	for index, gateway in enumerate(gateways):
		log_files.append(
			await aiofiles.open(
				f'log/engines/{c.EXPERIMENT_NAME}/instance-{gateway.port}-{datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")}.log',
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

		asyncio.create_task(
			process_simulator_logs(
				proc,
				log_files[index],
				gateway.port,
				simulator_ready_events[index],
			)
		)

		print(f'Engine started (PID: {simulators[index].pid}, PORT: {gateway.port}).')

	await orchestrate_matches(gateways, simulators, simulator_ready_events)
