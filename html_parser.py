from xml.sax.handler import ContentHandler
from xml.sax import parse


class TextHandler(ContentHandler):

    def startElement(self, name, attrs):
        if name == 'html':
            self.out = open('TestHandler.html', 'w')
            self.out.write('<html>')
        elif name != 'ix:nonNumeric' and name != 'ix:nonFraction':
            self.out.write('<' + name)
            for key, val in attrs.items():
                self.out.write(' {}="{}"'.format(key, val))
            self.out.write('>')

    def endElement(self, name):
        if name == 'html':
            self.out.write('</html>')
            self.out.close()
        elif name != 'ix:nonNumeric' and name != 'ix:nonFraction':
            self.out.write('</{}>'.format(name))

    def characters(self, chars):
        self.out.write(chars)


parse('0101010_honbun_jpcrp030000-asr-001_E04869-000_2020-03-31_01_2020-06-25_ixbrl.htm', TextHandler())
