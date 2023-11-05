import pytest as pt
from smppai.session import create_session, Session, SessionState
from smppai import config


MESSAGE_LONG = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor '
    'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis '
    'nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. '
    'Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu '
    'fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in '
    'culpa qui officia deserunt mollit anim id est laborum.'
)

MESSAGE_SHORT = 'Hello world!!'

MESSAGE_UTF = 'Zażółć gęślą jaźń'

@pt.fixture
def session() -> Session:
    return create_session(config.SMPP_URI)

def test_send_one_short(session: Session):
    with session as s:
        assert s.state == SessionState.BOUND_TRX
        s.send_message(src='aaa', dest='bbb', message=MESSAGE_SHORT)
    assert True

def test_send_one_long(session: Session):
    with session as s:
        assert s.state == SessionState.BOUND_TRX
        s.send_message(src='aaa', dest='bbb', message=MESSAGE_LONG)
    assert True
    
def _test_send_multiple(session: Session):
    import time
    with session as s:
        for i in range(3):
            m = 'Send multiple ' + str(i)
            s.send_message(src='aaa', dest='bbb', message=m)
            time.sleep(1)
    assert True
