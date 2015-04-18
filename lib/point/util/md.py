from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern
from markdown.util import etree

try:
    import re2 as re
except ImportError:
    import re

class CodeBacktick(Preprocessor):
    def run(self, lines):
        _code = False
        _cseq = ''

        for l in lines:
            m = re.match(r'^(?P<spaces>\s*)(?P<cseq>```|~~~)\s*(?P<lang>.*)$', l)
            if m:
                yield '\r'
                if not _code:
                    _code = True
                    _cseq = m.group('cseq')
                    if m.group('lang'):
                        yield '    #!%s\r' % m.group('lang')
                else:
                    if _cseq == m.group('cseq'):
                        _code = False
                        _cseq = ''
                    else:
                        yield l
                continue

            if _code:
                yield '    %s' % l
            else:
                yield l

class QuoteBlock(Preprocessor):
    def run(self, lines):
        qblock = False
        for l in lines:
            if l.startswith('>'):
                qblock = True

            elif qblock:
                qblock = False
                if l.strip():
                    yield '\r'

            yield l

        if qblock:
            yield '\r'

class SharpHeader(Preprocessor):
    def run(self, lines):
        return [u"\u0005%s" % l if re.match(r'^#+[a-z]', l) else l for l in lines]

class UrlColons(Preprocessor):
    ul = u"\u00a1-\uffff" # unicode letters range
    # IP patterns
    ipv4_re = ur'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = ur'\[[0-9a-f:\.]+\]'
    # Host patterns
    hostname_re = ur'[a-z' + self.ul + ur'0-9](?:[a-z' + self.ul + ur'0-9-]*[a-z' + self.ul + ur'0-9])?'
    domain_re = ur'(?:\.[a-z' + self.ul + ur'0-9]+(?:[a-z' + self.ul + ur'0-9-]*[a-z' + self.ul + ur'0-9]+)*)*'
    tld_re = ur'\.[a-z' + self.ul + ur']{2,}\.?'
    host_re = '(' + self.hostname_re + self.domain_re + self.tld_re + '|localhost)'

    url_re = (
            ur'(?P<scheme>([a-z0-9\.\-]*)://)'  # scheme is validated separately
            ur'(?P<auth>(\S+(?::\S*)?@)?)'  # user:pass authentication
            ur'(?P<host>(' + self.ipv4_re + '|' + self.ipv6_re + '|' + self.host_re + '))'
            ur'(?P<port>(:\d{2,5})?)'  # port
            ur'(?P<resourse>((?P<path>.+?)(?P<query>(\?(?P<qrysub>.+?))?)(?P<fragment>#(?P<frgsub>.+))?))\s'
            , re.IGNORECASE)

    def replace(self, m):
        return('%s%s%s%s%s%s%s' % (m.group('scheme'),
                m.group('auth'),
                m.group('host'),
                m.group('port'),
                m.group('path'),
                m.group('query'),
                re.sub(r':', '%3a', m.group('fragment'))))

    def run(self, lines):
        for l in lines:
            yield re.sub(self.url_re, self.replace, l)


class StrikePattern(Pattern):
    def __init__(self):
        Pattern.__init__(self, ur'~~(?!~)(?P<text>.+?)~~')

    def handleMatch(self, m):
        s = etree.Element('s')
        s.text = m.group('text')
        return s
