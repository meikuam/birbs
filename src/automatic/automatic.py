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

runner = BackgroundRunner()

# @app.on_event('startup')
# async def app_startup():
#     asyncio.create_task(runner.run())
#
#
# @app.get("/")
# def root():
#     return runner.value