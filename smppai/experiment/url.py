import dataclasses as dtc
import re

# import typing as tp
from urllib.parse import unquote


@dtc.dataclass(frozen=True)
class URL:
    protocol: str
    username: str
    password: str
    host: str
    port: int = 2775

    as_dict = dtc.asdict


def _parse_url(url: str) -> URL:
    pattern = re.compile(
        r'''
            (?P<protocol>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>[^@]*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/\?]+)\] |
                    (?P<ipv4host>[^/:\?]+)
                )?
                (?::(?P<port>[^/\?]*))?
            )?
            ''',
        re.X,
    )

    m = pattern.match(url)
    if m is not None:
        components = m.groupdict()

        if components['username'] is not None:
            components['username'] = _url_unquote(components['username'])

        if components['password'] is not None:
            components['password'] = _url_unquote(components['password'])

        ipv4host = components.pop('ipv4host')
        ipv6host = components.pop('ipv6host')
        components['host'] = ipv4host or ipv6host

        if components['port']:
            components['port'] = int(components['port'])
        else:
            components.pop('port')

        return URL(**components)

    else:
        raise AttributeError(f'Could not parse SMPP server URL from string "{url}"')


def _url_quote(text: str) -> str:
    return re.sub(r'[:@/]', lambda m: '%%%X' % ord(m.group(0)), text)


_url_unquote = unquote
