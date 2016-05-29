
import re
import codecs
from htmlentitydefs import name2codepoint, codepoint2name


encode_table = {unichr(code): "&%s;" % name for code, name in codepoint2name.iteritems()}
encode_regex = re.compile("(%s)" % "|".join(map(re.escape, encode_table.keys())))

decode_table = {"&%s;" % name: unichr(code) for name, code in name2codepoint.iteritems()}
decode_regex = re.compile("(?:&#(\d{1,5});)|(?:&#x(\d{1,5});)|(&\w{1,8};)")


class HtmlCodec(codecs.Codec):

    def encode(self, input, errors='strict'):
        output = encode_regex.sub(lambda match: encode_table[match.group(0)], input)
        return output, len(output)

    def decode(self, input, errors='strict'):
        def substitute(match):
            code, xcode, entity = match.group(1, 2, 3)
            return unichr(int(code)) if code else unichr(int(xcode, 16)) if xcode else decode_table.get(entity, entity)
        output = decode_regex.sub(substitute, input)
        return output, len(output)


class HtmlIncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        raise NotImplementedError


class HtmlIncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        raise NotImplementedError


class HtmlStreamReader(HtmlCodec, codecs.StreamReader):
    pass


class HtmlStreamWriter(HtmlCodec, codecs.StreamWriter):
    pass


def search(encoding):
    if encoding == 'html':
        return codecs.CodecInfo(name='html',
                encode=HtmlCodec().encode,
                decode=HtmlCodec().decode,
                incrementalencoder=HtmlIncrementalEncoder,
                incrementaldecoder=HtmlIncrementalDecoder,
                streamreader=HtmlStreamReader,
                streamwriter=HtmlStreamWriter)
    return None
