ENVIRONMENT = 'local'  # 'local' or 'production'

SERVER_HOST = '127.0.0.1'

SERVER_PORT = 2775

SMPP_URI = 'smpp://smppclient1:password@127.0.0.1:2775'

LOGGING_LEVEL = 'DEBUG'

SMPP_LOGGING_LEVEL = 'DEBUG'

# LOGGING_FORMAT = '[%(module)-10s:%(lineno)-3s]' '[%(thread)d] %(message)s'
LOGGING_FORMAT = '%(message)s'

LOGGING_DATEFORMAT = '%Y-%m-%d %H:%M:%S %z'

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
