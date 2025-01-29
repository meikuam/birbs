import asyncio


# https://github.com/tiangolo/fastapi/issues/2713
class BackgroundRunner:

    def __init__(self):
        self.running = False

    async def run(self):
        while True:
            await asyncio.sleep(0.5)
            if self.running:
                pass
