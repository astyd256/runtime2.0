
#define WRONG_CHARACTER 0


typedef enum
{
    WHITESPACE,             /* TAB, LF, CR, SPACE */
    EXCLAMATION,            /* ! */
    QUOTE,                  /* " */
    SHARP,                  /* # */
    AMPERSAND,              /* & */
    HYPHEN,                 /* - */
    SLASH,                  /* / */
    DIGIT,                  /* [0-9] */
    SEMICOLON,              /* ; */
    LESS,                   /* < */
    EQUAL,                  /* = */
    GREATER,                /* > */
    HEXADECIMAL_DIGIT,      /* [A-Fa-f] */
    LEFT_SQUARE_BRACKET,    /* [ */
    RIGHT_SQUARE_BRACKET,   /* ] */
    NAME_START_CHARACTER,   /* [A-Za-z] (HEXADECIMAL_DIGIT, X), '_' */
    X,                      /* Xx */
    NAME_CHARACTER,         /* NAME_START_CHARACTER, DIGIT */
    CHARACTER,              /* WHITESPACE, [#x21-#xD7FF], [#xE000-#xFFFD], [#x10000-#x10FFFF] */
    END,
    WRONG
}
Symbol;


static Symbol symbols[] = 
{
/* 0x00 */  WRONG,                   WRONG,                   WRONG,                   WRONG,
/* 0x04 */  WRONG,                   WRONG,                   WRONG,                   WRONG,
/* 0x08 */  WRONG,                   WHITESPACE,              WHITESPACE,              WRONG,
/* 0x0C */  WRONG,                   WHITESPACE,              WRONG,                   WRONG,
/* 0x10 */  WRONG,                   WRONG,                   WRONG,                   WRONG,
/* 0x14 */  WRONG,                   WRONG,                   WRONG,                   WRONG,
/* 0x18 */  WRONG,                   WRONG,                   WRONG,                   WRONG,
/* 0x1C */  WRONG,                   WRONG,                   WRONG,                   WRONG,

/* 0x20 */  WHITESPACE,              EXCLAMATION,             QUOTE,                   SHARP,
/* 0x24 */  CHARACTER,               CHARACTER,               AMPERSAND,               CHARACTER,
/* 0x28 */  CHARACTER,               CHARACTER,               CHARACTER,               CHARACTER,
/* 0x2C */  CHARACTER,               HYPHEN,                  CHARACTER,               SLASH,
/* 0x30 */  DIGIT,                   DIGIT,                   DIGIT,                   DIGIT,
/* 0x34 */  DIGIT,                   DIGIT,                   DIGIT,                   DIGIT,
/* 0x38 */  DIGIT,                   DIGIT,                   CHARACTER,               SEMICOLON,
/* 0x3C */  LESS,                    EQUAL,                   GREATER,                 CHARACTER,

/* 0x40 */  CHARACTER,               HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,
/* 0x44 */  HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       NAME_START_CHARACTER,
/* 0x48 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x4C */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x50 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x54 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x58 */  X,                       NAME_START_CHARACTER,    NAME_START_CHARACTER,    LEFT_SQUARE_BRACKET,
/* 0x5C */  CHARACTER,               RIGHT_SQUARE_BRACKET,    CHARACTER,               NAME_START_CHARACTER,

/* 0x60 */  CHARACTER,               HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,
/* 0x64 */  HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       HEXADECIMAL_DIGIT,       NAME_START_CHARACTER,
/* 0x68 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x6C */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x70 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x74 */  NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,    NAME_START_CHARACTER,
/* 0x78 */  X,                       NAME_START_CHARACTER,    NAME_START_CHARACTER,    CHARACTER,
/* 0x7C */  CHARACTER,               CHARACTER,               CHARACTER,               CHARACTER
};
