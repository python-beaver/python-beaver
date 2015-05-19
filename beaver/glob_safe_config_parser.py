# -*- coding: utf-8 -*-
import ConfigParser
import re

"""
Allows use of square brackets in .ini section names, which are used in some globs.
Based off of python 2.6 ConfigParser.RawConfigParser source code with a few modifications.
http://hg.python.org/cpython/file/8c4d42c0dc8e/Lib/configparser.py
"""
class GlobSafeConfigParser(ConfigParser.RawConfigParser):

    OPTCRE = re.compile(
        r'(?P<option>[^:=\s][^:=]*)'
        r'\s*(?P<vi>[:=])\s*'       
        r'(?P<value>.*)$'           
        )

    def _read(self, fp, fpname):
        cursect = None
        optname = None
        lineno = 0
        e = None
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                continue
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname] = "%s\n%s" % (cursect[optname], value)
            else:
                try:
                  value = line[:line.index(';')].strip()
                except ValueError:
                  value = line.strip()

                if  value[0]=='[' and value[-1]==']' and len(value)>2:
                    sectname = value[1:-1]
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == "DEFAULT":
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                    optname = None
                elif cursect is None:
                    raise ConfigParser.MissingSectionHeaderError(fpname, lineno, line)
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        if vi in ('=', ':') and ';' in optval:
                            pos = optval.find(';')
                            if pos != -1 and optval[pos-1].isspace():
                                optval = optval[:pos]
                        optval = optval.strip()
                        if optval == '""':
                            optval = ''
                        optname = self.optionxform(optname.rstrip())
                        cursect[optname] = optval
                    else:
                        if not e:
                            e = ConfigParser.ParsingError(fpname)
                        e.append(lineno, repr(line))
        if e:
            raise e
