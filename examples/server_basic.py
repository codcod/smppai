import asyncio

from smpp import SMPPServer


print('SMPP server listening on localhost:2775 (Ctrl+C to stop)')
asyncio.run(SMPPServer('localhost', 2775).serve_forever())
