# import threading

# from smpplib import consts
# from smpplib import gsm
from smpplib.client import Client

from smppai import config


class Session:
    _client: Client

    def __init__(self, system_id: str, password: str) -> None:
        self.system_id = system_id
        self.password = password

    def connect(self):
        self._client = Client(
            config.SERVER_HOST,
            config.SERVER_PORT,
            allow_unknown_opt_params=True,
            logger_name='smpp.Client',
            timeout=10,
        )
        self._client.connect()
        self._client.bind_transceiver(system_id=self.system_id, password=self.password)
        # self.thread = threading.Thread(target=self._client.listen)
        # self.thread.start()
        # self._client.listen()

    def send_message(self, *, src: str, dest: str, message: str):
        # parts, encoding_flag, msg_type_flag = gsm.make_parts(message)
        # for part in parts:
        #     pdu = self._client.send_message(
        #         source_addr=src,
        #         destination_addr=dest,
        #         short_message=part,
        #         data_coding=encoding_flag,
        #         esm_class=msg_type_flag,
        #         source_addr_ton=consts.SMPP_TON_INTL,
        #         dest_addr_ton=consts.SMPP_TON_INTL,
        #         registered_delivery=True,
        #     )
        #     print(f'{pdu=}')
        ...

    def disconnect(self):
        self._client.unbind()
        self._client.disconnect()

    def __enter__(self):
        print("Entering the context...")
        print(f'CREDENTIALS: {self.system_id=} {self.password=}')
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        print("Leaving the context...")
        # self.thread.join()
        self.disconnect()
