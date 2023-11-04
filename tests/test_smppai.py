import pytest as pt
from smppai.experiment.session import Session


@pt.fixture
def session() -> Session:
    return Session(system_id='smppclient1', password='password')


def test_send_one(session: Session):
    with session:
        session.send_message(sender='aaa', recipient='bbb', message='Hi')

# def test_send_batch_many_small(connector: Connector):
#     with connector as conn:
#         for _ in range(1_000):
#             m = Message()
#             conn.batch(m)
#         conn.flush()
