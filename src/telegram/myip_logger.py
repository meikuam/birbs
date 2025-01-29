import logging
import asyncio
import public_ip as ip
from src.telegram.bot import send_message, chat_ids


class MyIPLogger:

    def __init__(self, wait_time=600):
        self.wait_time = wait_time
        self.running = True
        self.current_ip = None
    
    async def run(self):
        while True:
            try:    
                myip = ip.get()
                if self.current_ip != myip:
                    await send_message(chat_ids[0], myip)
                    self.current_ip = myip
                    logging.info(f"cool: {self.current_ip}")
            except Exception as e:
                logging.error(exc_info=e)
            await asyncio.sleep(self.wait_time)


if __name__ == "__main__":
    my_ip_logger = MyIPLogger()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(my_ip_logger.run())
