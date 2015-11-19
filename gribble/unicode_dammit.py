# -*- coding: utf-8 -*-
import os
import codecs

CHARSET_ALIASES = {'macintosh': 'mac-roman', 'x-sjis': 'shift-jis'}
ENCODINGS = [
    'windows-1252',
    'iso-8859-1',
    'iso-8859-2',
]


def unicode_dammit(string, logger=None):
    for encoding in ENCODINGS:
        try:
            string = string.strip(os.linesep)
        except UnicodeDecodeError:
            u = _convert_from(string, encoding)
            if u:
                string = u
                break

    return string


def _convert_from(markup, proposed, errors='strict'):
    proposed = _find_codec(proposed)

    try:
        u = _to_unicode(markup, proposed, errors)
        markup = u
    except Exception:
        return None

    return markup


def _to_unicode(self, data, encoding, errors='strict'):
    '''Given a string and its encoding, decodes the string into Unicode.
    %encoding is a string recognized by encodings.aliases'''

    # strip Byte Order Mark (if present)
    if (len(data) >= 4) and (data[:2] == '\xfe\xff') and (data[2:4] != '\x00\x00'):
        encoding = 'utf-16be'
        data = data[2:]
    elif (len(data) >= 4) and (data[:2] == '\xff\xfe') and (data[2:4] != '\x00\x00'):
        encoding = 'utf-16le'
        data = data[2:]
    elif data[:3] == '\xef\xbb\xbf':
        encoding = 'utf-8'
        data = data[3:]
    elif data[:4] == '\x00\x00\xfe\xff':
        encoding = 'utf-32be'
        data = data[4:]
    elif data[:4] == '\xff\xfe\x00\x00':
        encoding = 'utf-32le'
        data = data[4:]
    newdata = unicode(data, encoding, errors)
    return newdata


def _find_codec(self, charset):
    return _codec(CHARSET_ALIASES.get(charset, charset)) \
        or (charset and self._codec(charset.replace('-', ''))) \
        or (charset and self._codec(charset.replace('-', '_'))) \
        or charset


def _codec(self, charset):
    if not charset:
        return charset
    codec = None
    try:
        codecs.lookup(charset)
        codec = charset
    except (LookupError, ValueError):
        pass
    return codec
