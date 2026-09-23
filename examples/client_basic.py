import asyncio

from smpp import SMPPClient


async def main():
    async with SMPPClient('localhost', 2775, 'test_client', 'password') as client:
        await client.bind_transmitter()
        message_id = await client.submit_sm('12345', '67890', 'Hello World!')
        print(f'Sent, message ID: {message_id}')


asyncio.run(main())
