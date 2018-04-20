
#define DECIMAL(character) (character - '0')
#define HEXADECIMAL(character) (character < 'A' ? character - '0' \
    : character < 'a' ? character - 'A' + 10 : character - 'a' + 10)
#define LETTER(character) (character >= 'A' && character <= 'Z' ? character - 'A' + 10 \
    : character >= 'a' && character <= 'z' ? character - 'a' + 10 \
    : character >= '0' && character <= '9' ? character - '0' : 0x3F)


static Character
lookup_entity(Hash hash, Length length)
{
    if (length > 5)
        return 0;

    switch (hash)
    {
    case 0x0000055D: /* lt */
        return '<';
    case 0x0000041D: /* gt */
        return '>';
    case 0x0000A599: /* amp */
        return '&';
    case 0x0029961C: /* apos */
        return '\'';
    case 0x0069E61D: /* quot */
        return '"';
    default:
        return 0;
    }
}
