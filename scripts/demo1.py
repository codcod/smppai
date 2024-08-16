import argparse
import asyncio

from smppai.session import Session
from smppai.session import create_session


async def send_messages(
    session: Session, *, src: str, dest: str, message: str, count: int
):
    async with session as s:
        i = 0
        while True:
            await s.send_message(src=src, dest=dest, message=f'{message}:{i}')
            i = i + 1
            if i > count:
                break
            print('message sent')
            
            # await asyncio.sleep(1)


async def receive_messages(session: Session):
    await asyncio.sleep(3)
    async for msg in session:
        print(f'got {msg}')


async def demo(args):
    sess = create_session('smpp://smppclient1:password@127.0.0.1:2775')
    await asyncio.gather(
        send_messages(
            sess, src=args.src, dest=args.dest, message=args.message, count=args.count
        ),
        receive_messages(sess),
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src', type=str, default='+48123456789')
    parser.add_argument('--dest', type=str, default='+48999999999')
    parser.add_argument('--message', type=str, default='Hello world!')
    parser.add_argument('--count', type=int, default=100)
    args = parser.parse_args()
    try:
        asyncio.run(demo(args))
    except KeyboardInterrupt:
        print('Bye!')
