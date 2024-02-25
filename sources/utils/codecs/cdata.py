
import codecs


class XmlCodec(codecs.Codec):

    def encode(self, input, errors='strict'):
        output = u"<![CDATA[%s]]>" % input.replace("]]>", "]]]]><![CDATA[>")
        # TODO: As of my understanding now encoding only needed to work with bytes,
        #  so the whole logic should be rewritten
        return output.encode("utf-8"), len(output)

    def decode(self, input, errors='strict'):
        raise NotImplementedError


class XmlIncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        raise NotImplementedError


class XmlIncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        raise NotImplementedError


class XmlStreamReader(XmlCodec, codecs.StreamReader):
    pass


class XmlStreamWriter(XmlCodec, codecs.StreamWriter):
    pass


def search(encoding):
    if encoding == 'cdata':
        return codecs.CodecInfo(name='cdata',
                encode=XmlCodec().encode,
                decode=XmlCodec().decode,
                incrementalencoder=XmlIncrementalEncoder,
                incrementaldecoder=XmlIncrementalDecoder,
                streamreader=XmlStreamReader,
                streamwriter=XmlStreamWriter)
    return None
