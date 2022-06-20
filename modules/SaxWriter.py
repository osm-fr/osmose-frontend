from xml.sax.saxutils import XMLGenerator, quoteattr


class SaxWriter(XMLGenerator):
    def __init__(self, out, enc):
        if type(out) == str:
            XMLGenerator.__init__(self, open(out, "w"), enc)
        else:
            XMLGenerator.__init__(self, out, enc)

    def startElement(self, name, attrs={}):
        self._write("<" + name)
        for (name, value) in attrs.items():
            self._write(" %s=%s" % (name, quoteattr(value)))
        self._write(">\n")

    def endElement(self, name):
        self._write("</%s>\n" % name)

    def Element(self, name, attrs={}):
        self._write("<" + name)
        for (name, value) in attrs.items():
            self._write(" %s=%s" % (name, quoteattr(value)))
        self._write(" />\n")
