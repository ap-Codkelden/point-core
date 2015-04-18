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
    hostname_re = ur'[a-z' + ul + ur'0-9](?:[a-z' + ul + ur'0-9-]*[a-z' + ul + ur'0-9])?'
    domain_re = ur'(?:\.[a-z' + ul + ur'0-9]+(?:[a-z' + ul + ur'0-9-]*[a-z' + ul + ur'0-9]+)*)*'
    tld_re = ur'\.[a-z' + ul + ur']{2,}\.?'
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    url_re = re.compile(
        ur'(?P<scheme>((\w+)://))'
        ur'(?P<pass>(\S+(?::\S*)?@)?)' 
        ur'(?P<authority>([^/?#]*)?)'
        ur'(?P<undef>([^?#]*)?)'
        ur'(?P<query>(\?([^#]*))?)'
        ur'(?P<fragment>(#(\S+))?)'
        , re.IGNORECASE)

    def replace(self, m):
        return '%s%s%s%s%s%s' % (m.group('scheme'),
            m.group('pass'),
            m.group('authority'),
            m.group('undef'),
            m.group('query'),
            re.sub(r':', '%3a', m.group('fragment')))

    def run(self, lines):
        for l in lines:
            #yield self.url_re.sub(self.replace, l)
            yield re.sub(self.url_re, self.replace, l)


class StrikePattern(Pattern):
    def __init__(self):
        Pattern.__init__(self, ur'~~(?!~)(?P<text>.+?)~~')

    def handleMatch(self, m):
        s = etree.Element('s')
        s.text = m.group('text')
        return s
