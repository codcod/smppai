import asyncio

import smpp


async def main():
    async with smpp.connect('localhost', 2775, 'smppclient1', 'password') as client:
        result = await client.send('67890', 'Hello World!', sender='12345')
        print(f'Sent, message IDs: {result.message_ids}')


asyncio.run(main())
