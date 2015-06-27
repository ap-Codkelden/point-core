# -*- coding: utf-8 -*-

"""
Unique Footnotes Extension for Python-Markdown
=======================================

Adds unique footnote handling to Python-Markdown.

See <https://pythonhosted.org/Markdown/extensions/footnotes.html>
for documentation.

Copyright The Python Markdown Project

License: [BSD](http://www.opensource.org/licenses/bsd-license.php)

ампутирован unique_prefix 
unique_ids

"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.inlinepatterns import Pattern
from markdown.treeprocessors import Treeprocessor
from markdown.postprocessors import Postprocessor
from markdown.util import etree, text_type
from markdown.odict import OrderedDict
import re
from random import choice
from string import lowercase

FN_BACKLINK_TEXT = "zz1337820767766393qq"
NBSP_PLACEHOLDER = "qq3936677670287331zz"
DEF_RE = re.compile(r'[ ]{0,3}\[\^([^\]]*)\]:\s*(.*)')
TABBED_RE = re.compile(r'((\t)|(    ))(.*)')

def _unique_id():
    return ''.join(choice(lowercase) for i in range(6))

class UniqueFootnoteExtension(Extension):
    """ Unique Footnote Extension. """

    def __init__(self, *args, **kwargs):
        """ Setup configs. """

        self.config = {
            'PLACE_MARKER':
                ["///Footnotes Go Here///",
                 "The text string that marks where the footnotes go"],
            "BACKLINK_TEXT":
                ["&#8617;",
                 "The text string that links from the footnote "
                 "to the reader's place."]
        }
        super(UniqueFootnoteExtension, self).__init__(*args, **kwargs)
        
        self.unique_prefix = 0
        self.reset()

    def extendMarkdown(self, md, md_globals):
        """ Add pieces to Markdown. """
        md.registerExtension(self)
        self.parser = md.parser
        self.md = md
        # Insert a preprocessor before ReferencePreprocessor
        md.preprocessors.add(
            "footnote", FootnotePreprocessor(self), "<reference"
        )
        # Insert an inline pattern before ImageReferencePattern
        FOOTNOTE_RE = r'\[\^([^\]]*)\]'  # blah blah [^1] blah
        md.inlinePatterns.add(
            "footnote", FootnotePattern(FOOTNOTE_RE, self), "<reference"
        )
        # Insert a tree-processor that would actually add the footnote div
        # This must be before all other treeprocessors (i.e., inline and
        # codehilite) so they can run on the the contents of the div.
        md.treeprocessors.add(
            "footnote", FootnoteTreeprocessor(self), "_begin"
        )
        # Insert a postprocessor after amp_substitute oricessor
        md.postprocessors.add(
            "footnote", FootnotePostprocessor(self), ">amp_substitute"
        )

    def reset(self):
        """ Clear footnotes on reset, and prepare for distinct document. """
        self.footnotes = OrderedDict()
        self.unique_prefix += 1

    def findFootnotesPlaceholder(self, root):
        """ Return ElementTree Element that contains Footnote placeholder. """
        def finder(element):
            for child in element:
                if child.text:
                    if child.text.find(self.getConfig("PLACE_MARKER")) > -1:
                        return child, element, True
                if child.tail:
                    if child.tail.find(self.getConfig("PLACE_MARKER")) > -1:
                        return child, element, False
                finder(child)
            return None

        res = finder(root)
        return res

    def setFootnote(self, id, text):
        """ Store a footnote for later retrieval. """
        self.footnotes[id] = _unique_id(), text

    def get_separator(self):
        if self.md.output_format in ['html5', 'xhtml5']:
            return '-'
        return ':'

    def makeFootnoteId(self, id):
        """ Return footnote link id. """
        return 'fn%s%s%s' % (self.get_separator(),  self.footnotes[id][0])

    def makeFootnoteRefId(self, id):
        """ Return footnote back-link id. """
        return 'fnref%s%s%s' % (self.get_separator(), self.footnotes[id][0])

    def makeFootnotesDiv(self, root):
        """ Return div of footnotes as et Element. """

        if not list(self.footnotes.keys()):
            return None

        div = etree.Element("div")
        div.set('class', 'footnote')
        etree.SubElement(div, "hr")
        ol = etree.SubElement(div, "ol")

        for id in self.footnotes.keys():
            li = etree.SubElement(ol, "li")
            li.set("id", self.makeFootnoteId(id))
            self.parser.parseChunk(li, self.footnotes[id][1])
            backlink = etree.Element("a")
            backlink.set("href", "#" + self.makeFootnoteRefId(id))
            if self.md.output_format not in ['html5', 'xhtml5']:
                backlink.set("rev", "footnote")  # Invalid in HTML5
            backlink.set("class", "footnote-backref")
            backlink.set(
                "title",
                "Jump back to footnote %d in the text" %
                (self.footnotes.index(id)+1)
            )
            backlink.text = FN_BACKLINK_TEXT

            if li.getchildren():
                node = li[-1]
                if node.tag == "p":
                    node.text = node.text + NBSP_PLACEHOLDER
                    node.append(backlink)
                else:
                    p = etree.SubElement(li, "p")
                    p.append(backlink)
        return div


class FootnotePreprocessor(Preprocessor):
    """ Find all footnote references and store for later use. """

    def __init__(self, footnotes):
        self.footnotes = footnotes

    def run(self, lines):
        """
        Loop through lines and find, set, and remove footnote definitions.

        Keywords:

        * lines: A list of lines of text

        Return: A list of lines of text with footnote definitions removed.

        """
        newlines = []
        i = 0
        while True:
            m = DEF_RE.match(lines[i])
            if m:
                fn, _i = self.detectTabbed(lines[i+1:])
                fn.insert(0, m.group(2))
                i += _i-1  # skip past footnote
                self.footnotes.setFootnote(m.group(1), "\n".join(fn))
            else:
                newlines.append(lines[i])
            if len(lines) > i+1:
                i += 1
            else:
                break
        return newlines

    def detectTabbed(self, lines):
        """ Find indented text and remove indent before further proccesing.

        Keyword arguments:

        * lines: an array of strings

        Returns: a list of post processed items and the index of last line.

        """
        items = []
        blank_line = False  # have we encountered a blank line yet?
        i = 0  # to keep track of where we are

        def detab(line):
            match = TABBED_RE.match(line)
            if match:
                return match.group(4)

        for line in lines:
            if line.strip():  # Non-blank line
                detabbed_line = detab(line)
                if detabbed_line:
                    items.append(detabbed_line)
                    i += 1
                    continue
                elif not blank_line and not DEF_RE.match(line):
                    # not tabbed but still part of first par.
                    items.append(line)
                    i += 1
                    continue
                else:
                    return items, i+1

            else:  # Blank line: _maybe_ we are done.
                blank_line = True
                i += 1  # advance

                # Find the next non-blank line
                for j in range(i, len(lines)):
                    if lines[j].strip():
                        next_line = lines[j]
                        break
                else:
                    break  # There is no more text; we are done.

                # Check if the next non-blank line is tabbed
                if detab(next_line):  # Yes, more work to do.
                    items.append("")
                    continue
                else:
                    break  # No, we are done.
        else:
            i += 1

        return items, i


class FootnotePattern(Pattern):
    """ InlinePattern for footnote markers in a document's body text. """

    def __init__(self, pattern, footnotes):
        super(FootnotePattern, self).__init__(pattern)
        self.footnotes = footnotes


    def handleMatch(self, m):
        id = m.group(2)
        if id in self.footnotes.footnotes.keys():
            sup = etree.Element("sup")
            a = etree.SubElement(sup, "a")
            sup.set('id', self.footnotes.makeFootnoteRefId(id))
            a.set('href', '#' + self.footnotes.makeFootnoteId(id))
            if self.footnotes.md.output_format not in ['html5', 'xhtml5']:
                a.set('rel', 'footnote')  # invalid in HTML5
            a.set('class', 'footnote-ref')
            a.text = text_type(self.footnotes.footnotes.index(id) + 1)
            return sup
        else:
            return None


class FootnoteTreeprocessor(Treeprocessor):
    """ Build and append footnote div to end of document. """

    def __init__(self, footnotes):
        self.footnotes = footnotes

    def run(self, root):
        footnotesDiv = self.footnotes.makeFootnotesDiv(root)
        if footnotesDiv is not None:
            result = self.footnotes.findFootnotesPlaceholder(root)
            if result:
                child, parent, isText = result
                ind = parent.getchildren().index(child)
                if isText:
                    parent.remove(child)
                    parent.insert(ind, footnotesDiv)
                else:
                    parent.insert(ind + 1, footnotesDiv)
                    child.tail = None
            else:
                root.append(footnotesDiv)


class FootnotePostprocessor(Postprocessor):
    """ Replace placeholders with html entities. """
    def __init__(self, footnotes):
        self.footnotes = footnotes

    def run(self, text):
        text = text.replace(
            FN_BACKLINK_TEXT, self.footnotes.getConfig("BACKLINK_TEXT")
        )
        return text.replace(NBSP_PLACEHOLDER, "&#160;")


def makeExtension(*args, **kwargs):
    """ Return an instance of the FootnoteExtension """
    return FootnoteExtension(*args, **kwargs)