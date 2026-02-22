import asyncio
from KickAI import KickAI
from DisplayInfo import DisplayInfo

from pyftg.socket.aio.gateway import Gateway

gateway = Gateway(port=8000)

async def start_process():
    agent1 = KickAI()
    agent2 = DisplayInfo()
    gateway.register_ai("KickAI", agent1)
    gateway.register_ai("DisplayInfo", agent2)
    game_name = f"{"adhoc"}-instance-{0}-{agent1.name()}-vs-{agent2.name()}"

    await gateway.run_game([f"{game_name}<name>ZEN", "ZEN"], ["KickAI", "DisplayInfo"], 5)

    await gateway.close()
    
asyncio.run(start_process())