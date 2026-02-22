import asyncio
from pyftg.socket.aio.gateway import Gateway

async def main():
    gateway = Gateway(port=31415) # Default port for DareFightingICE 7.0
    agent = MyAgent()
    
    gateway.register_ai("MyPythonAI", agent)
    # This will wait for the Java engine to start a match
    await gateway.run_game(["ZEN", "ZEN"], ["MyPythonAI", "MctsAi"], 1)

if __name__ == "__main__":
    asyncio.run(main())