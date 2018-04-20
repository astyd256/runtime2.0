
#define PASS {KEEP}
#define ERROR {FAILURE, wrong_character}

#define PARSE_ELEMENT_CONTENT CONTENT_CONTINUATION
#define PARSE_ATTRIBUTE_VALUE ATTRIBUTE_VALUE

#define ASSERT(condition, message, ...) \
    if (!(condition)) \
    { \
        __VA_ARGS__; \
        PyErr_SetString(PyExc_RuntimeError, message); \
        return FAILURE; \
    }


static State
wrong_character(Parse *parse)
{
    if (parse->symbol == END)
        PyErr_SetString(WrongCharacterError, "Unexpected end of document");
    else
        PyErr_Format(WrongCharacterError, "Wrong character '%c' (0x%x)",
            (parse->character < ' ' || parse->character == '\'' || parse->character > '~') ? '?'
                : parse->character, parse->character);
    return FAILURE;
}

static State
mark_character(Parse *parse)
{
    parse->mark = parse->data;
    return NEXT;
}

static State
complete(Parse *parse)
{
    if (parse->element->parent)
    {
        PyErr_SetString(UnableToParseError, "Unexpected end of document");
        return FAILURE;
    }
    return NEXT;
}


/* Element */

static State
open_element(Parse *parse)
{
    Element *element;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object,
        "Missing element object")
#endif

    element = new_element(parse);
    if (!element)
        return FAILURE;

    parse->mark = parse->data;
    return NEXT;
}

static State
close_element_name(Parse *parse)
{
    PyObject **reference;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object")
#endif

    if (parse->match_string(parse->mark, parse->data, "attribute"))
    {
        parse->element->type = AttributeElement;
        if (!parse->element->parent)
        {
            PyErr_SetString(UnableToParseError, "Misplaced attribute element");
            return FAILURE;
        }
    }

    switch (parse->element->type)
    {
    case GenericElement:
        parse->element->name = parse->create_python_string(parse->mark, parse->data);
        parse->element->object = \
            create_new_memory_object(parse->element->parent->object, parse->element->name);
        if (!parse->element->object)
            return FAILURE;

        reference = new_reference(parse);
        if (!reference)
            return FAILURE;

        *reference = hold_python_object(parse->element->object);

        if (!parse->element->parent->parent)
        {
            if (parse->result)
            {
                PyErr_SetString(UnableToParseError, "Multiple root elements");
                return FAILURE;
            }
            parse->result = hold_python_object(parse->element->object);
        }

        return NEXT;
    case AttributeElement:
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
open_element_close_name(Parse *parse)
{
    parse->mark = parse->data;
    return NEXT;
}

static State
open_element_content(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch (parse->element->type)
    {
    case GenericElement:
        return NEXT;
    case AttributeElement:
        if (reset_substrings(parse))
            return FAILURE;
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
close_element_name_and_open_content(Parse *parse)
{
    State state = close_element_name(parse);
    if (state)
        return state;
    return open_element_content(parse);
}

static State
start_element_substring(Parse *parse)
{
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch (parse->element->type)
    {
    case GenericElement:
        PyErr_SetString(WrongCharacterError, "Misplaced text");
        return FAILURE;
    case AttributeElement:
        substring = new_substring(parse);
        if (!substring)
            return FAILURE;
        substring->data = parse->data;
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
start_element_substring_from_mark(Parse *parse)
{
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch (parse->element->type)
    {
    case GenericElement:
        PyErr_SetString(WrongCharacterError, "Misplaced text");
        return FAILURE;
    case AttributeElement:
        substring = new_substring(parse);
        if (!substring)
            return FAILURE;
        substring->data = parse->mark;
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
end_element_substring(Parse *parse)
{
    DataSize size;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->type == AttributeElement,
        "Substring in non-attribute element")
    ASSERT(parse->substrings.list && parse->substrings.last,
        "Missing substring")
#endif

    size = parse->data - parse->substrings.last->data;
    parse->substrings.last->size = size;
    parse->substrings.size += size;
    return NEXT;
}

static State
start_element_substring_from_mark_and_end(Parse *parse)
{
    State state = start_element_substring_from_mark(parse);
    if (state)
        return 1;
    return end_element_substring(parse);
}

static State
close_element(Parse *parse)
{
    PyObject *value;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object");
    ASSERT(parse->element->attributes || parse->element->type != AttributeElement,
        "Missing attribute element name")
#endif

    switch (parse->element->type)
    {
    case GenericElement:

        /* for generic elements parse->element->attributes contains
           python dictionary with element attributes */

        if (parse->element->attributes)
        {
            if (update_memory_object_attributes(parse->element->object, parse->element->attributes))
                return FAILURE;
        }
        release_element(parse);
        return NEXT;
    case AttributeElement:

        /* for attribute elements parse->element->attributes contains
           python string - value of name attribute because we have not
           any other attributes for such elements:
           <ATTRIBUTE NAME="parse->element->attributes">value</ATTRBIUTE> */

        if (!parse->element->attributes)
        {
            PyErr_SetString(UnableToParseError, "Missing name attribute");
            return FAILURE;
        }

        if (parse->substrings.list)
        {
            value = parse->create_python_string_from_substrings(&parse->substrings);
            if (!value)
                return FAILURE;
            cleanup_substrings(parse);
        }
        else
        {
            value =  parse->create_empty_python_string();
            if (!value)
                return FAILURE;
        }

        if (parse->python_string_is_equal_to_string(parse->element->attributes, "name"))
        {
            if (set_memory_object_name(parse->element->parent->object, value))
            {
                release_python_object(value);
                return FAILURE;
            }
        }
        else
        {
            if (create_or_update_python_dictionary(
                &parse->element->parent->attributes, parse->element->attributes, value))
            {
                release_python_object(value);
                return FAILURE;
            }
        }
        release_python_object(value);
        release_element(parse);
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
close_element_and_check_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
#endif

    switch (parse->element->type)
    {
    case GenericAttribute:
        if (!parse->is_equal_to_python_string(parse->mark, parse->data, parse->element->name))
        {
            PyErr_SetString(NameDoesNotMatchError, "Element name does not match");
            return FAILURE;
        }
        return close_element(parse);
    case AttributeElement:
        if (!parse->match_string(parse->mark, parse->data, "attribute"))
        {
            PyErr_SetString(NameDoesNotMatchError, "Element name does not match");
            return FAILURE;
        }
        return close_element(parse);
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}


/* Attribute */

static State
open_attribute(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
#endif

    if (reset_attribute(parse))
        return FAILURE;
    if (reset_substrings(parse))
        return FAILURE;
    parse->mark = parse->data;
    return NEXT;
}

static State
close_attribute_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
#endif

    if (parse->match_string(parse->mark, parse->data, "name"))
        parse->attribute.type = NameAttribute;

    switch (parse->element->type)
    {
    case GenericElement:
        switch (parse->attribute.type)
        {
        case GenericAttribute:

            /* we store names for generic attributes */

            parse->attribute.name = parse->create_python_string(parse->mark, parse->data);
            if (!parse->attribute.name)
                return FAILURE;
            return NEXT;
        case NameAttribute:

            /* there is no need to store names for name attributes
               because we already know them */

            return NEXT;
#ifdef DEBUG
        default:
            PyErr_SetString(PyExc_RuntimeError, "Wrong attribute type");
            return FAILURE;
#endif
        }
    case AttributeElement:

        /* there is no need to store name for attribute element
           because there is only name attributes allowed here */

        if (parse->attribute.type != NameAttribute)
        {
            PyErr_SetString(UnableToParseError, "Irrelevant attribute");
            return FAILURE;
        }
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    };
}

static State
start_attribute_substring(Parse *parse)
{
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
#endif

    substring = new_substring(parse);
    if (!substring)
        return FAILURE;

    substring->data = parse->data;
    return NEXT;
}

static State
end_attribute_substring(Parse *parse)
{
    DataSize size;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
    ASSERT(parse->substrings.list && parse->substrings.last,
        "Missing substring")
#endif

    size = parse->data - parse->substrings.last->data;
    parse->substrings.last->size = size;
    parse->substrings.size += size;
    return NEXT;
}

static State
close_attribute(Parse *parse)
{
    PyObject *value;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->object
            || parse->element->type != GenericElement,
        "Missing element object")
    ASSERT(parse->attribute.type == NameAttribute
            || parse->element->type != AttributeElement,
        "Wrong attribute type")
    ASSERT(parse->attribute.name
            || parse->attribute.type == NameAttribute
            || parse->element->type != GenericElement,
        "Missing attribute name")
#endif

    if (parse->substrings.list)
    {
        value = parse->create_python_string_from_substrings(&parse->substrings);
        if (!value)
            return FAILURE;
        cleanup_substrings(parse);
    }
    else
    {
        value =  parse->create_empty_python_string();
        if (!value)
            return FAILURE;
    }

    switch (parse->element->type)
    {
    case GenericElement:
        switch (parse->attribute.type)
        {
        case GenericAttribute:

            /* we have non-name attribute with value and all we need
               is to store one in attributes and create ones if necessary */

            if (create_or_update_python_dictionary(
                &parse->element->attributes, parse->attribute.name, value))
            {
                release_python_object(value);
                return FAILURE;
            }
            release_python_object(value);
            cleanup_attribute(parse);
            return NEXT;
        case NameAttribute:

            /* we have name attribute and must assign it to element object */

            if (set_memory_object_name(parse->element->object, value))
            {
                release_python_object(value);
                return FAILURE;
            }
            release_python_object(value);
            return NEXT;
#ifdef DEBUG
        default:
            release_python_object(value);
            PyErr_SetString(PyExc_RuntimeError, "Wrong attribute type");
            return FAILURE;
#endif
        }
    case AttributeElement:

        /* we can have only name attribute here and currently we do not control
           attribute duplicates so just release previous value if any,
           so for attribute element we do not store attributes dictionary
           and store name value directly in parse->element->attributes */

        if (parse->element->attributes)
            release_python_object(parse->element->attributes);
        parse->element->attributes = value;
        return NEXT;
#ifdef DEBUG
    default:
        release_python_object(value);
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
close_attribute_and_end_substring(Parse *parse)
{
    State state = end_attribute_substring(parse);
    if (state)
        return state;
    return close_attribute(parse);
}


/* Entity */

static State
scan_entity_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->return_state == PARSE_ELEMENT_CONTENT
            || parse->return_state == PARSE_ATTRIBUTE_VALUE,
        "Wrong return state")
    ASSERT(parse->element->type == AttributeElement
            || parse->return_state != PARSE_ELEMENT_CONTENT,
        "Entity in non-attribute element")
#endif

    parse->entity.hash = (parse->entity.hash << 6) + LETTER(parse->character);
    parse->entity.length++;
    return NEXT;
}

static State
open_entity_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch(parse->return_state)
    {
    case PARSE_ELEMENT_CONTENT:
        if (parse->element->type != AttributeElement)
        {
            PyErr_SetString(WrongCharacterError, "Misplaced entity");
            return FAILURE;
        }
    case PARSE_ATTRIBUTE_VALUE:
        break;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong return state");
        return FAILURE;
#endif
    }

    parse->entity.hash = 0;
    parse->entity.length = 0;
    return scan_entity_name(parse);
}

static State
close_entity_name(Parse *parse)
{
    Character character;
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->return_state == PARSE_ELEMENT_CONTENT
            || parse->return_state == PARSE_ATTRIBUTE_VALUE,
        "Wrong return state")
    ASSERT(parse->element->type == AttributeElement
            || parse->return_state != PARSE_ELEMENT_CONTENT,
        "Entity in non-attribute element")
#endif

    character = lookup_entity(parse->entity.hash, parse->entity.length);
    if (!character)
    {
        PyErr_SetString(WrongCharacterError, "Wrong entity reference");
        return FAILURE;
    }

    substring = new_substring(parse);
    if (!substring)
        return FAILURE;

    substring->data = substring->buffer;
    substring->size = parse->write_character(substring->data, character);
    if (substring->size == 0)
        return FAILURE;

    parse->substrings.size += substring->size;
    return NEXT;
}


static State
scan_entity_code(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->return_state == PARSE_ELEMENT_CONTENT
            || parse->return_state == PARSE_ATTRIBUTE_VALUE,
        "Wrong return state")
    ASSERT(parse->element->type == AttributeElement
            || parse->return_state != PARSE_ELEMENT_CONTENT,
        "Entity in non-attribute element")
#endif

    parse->entity.character = parse->entity.character * 10 + DECIMAL(parse->character);
    parse->entity.length++;
    return NEXT;
}

static State
open_entity_code(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch(parse->return_state)
    {
    case PARSE_ELEMENT_CONTENT:
        if (parse->element->type != AttributeElement)
        {
            PyErr_SetString(WrongCharacterError, "Misplaced entity");
            return FAILURE;
        }
    case PARSE_ATTRIBUTE_VALUE:
        break;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong return state");
        return FAILURE;
#endif
    }

    parse->entity.character = 0;
    parse->entity.length = 0;
    return scan_entity_code(parse);
}


static State
scan_entity_hexadecimal_code(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->return_state == PARSE_ELEMENT_CONTENT
            || parse->return_state == PARSE_ATTRIBUTE_VALUE,
        "Wrong return state")
    ASSERT(parse->element->type == AttributeElement
            || parse->return_state != PARSE_ELEMENT_CONTENT,
        "Entity in non-attribute element")
#endif

    parse->entity.character = parse->entity.character * 16 + HEXADECIMAL(parse->character);
    parse->entity.length++;
    return NEXT;
}

static State
open_entity_hexadecimal_code(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
#endif

    switch(parse->return_state)
    {
    case PARSE_ELEMENT_CONTENT:
        if (parse->element->type != AttributeElement)
        {
            PyErr_SetString(WrongCharacterError, "Misplaced entity");
            return FAILURE;
        }
    case PARSE_ATTRIBUTE_VALUE:
        break;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong return state");
        return FAILURE;
#endif
    }

    parse->entity.character = 0;
    parse->entity.length = 0;
    return scan_entity_hexadecimal_code(parse);
}

static State
close_entity_code(Parse *parse)
{
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->return_state == PARSE_ELEMENT_CONTENT
            || parse->return_state == PARSE_ATTRIBUTE_VALUE,
        "Wrong return state")
    ASSERT(parse->element->type == AttributeElement
            || parse->return_state != PARSE_ELEMENT_CONTENT,
        "Entity in non-attribute element")
#endif

    if (parse->entity.length > 7)
    {
        PyErr_SetString(UnableToParseError, "Too big entity code point");
        return FAILURE;
    }

    substring = new_substring(parse);
    if (!substring)
        return FAILURE;

    substring->data = substring->buffer;
    substring->size = parse->write_character(substring->data, parse->entity.character);
    if (substring->size == 0)
        return FAILURE;

    parse->substrings.size += substring->size;
    return NEXT;
}


/* Character Data */

static State
open_cdata_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object");
#endif

    switch (parse->element->type)
    {
    case GenericElement:
        PyErr_SetString(WrongCharacterError, "Misplaced character data");
        return FAILURE;
    case AttributeElement:
        parse->mark = parse->data;
        return NEXT;
#ifdef DEBUG
    default:
        PyErr_SetString(PyExc_RuntimeError, "Wrong element type");
        return FAILURE;
#endif
    }
}

static State
close_cdata_name(Parse *parse)
{
#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object");
    ASSERT(parse->element->type == AttributeElement,
        "Character data in non-attribute element")
#endif

    if (!parse->is_equal_to_string(parse->mark, parse->data, "CDATA"))
    {
        PyErr_SetString(WrongCharacterError, "Wrong character data start sequence");
        return FAILURE;
    }
    return NEXT;
}

static State
start_cdata_substring(Parse *parse)
{
    Substring *substring;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object");
    ASSERT(parse->element->type == AttributeElement,
        "Character data in non-attribute element")
#endif

    substring = new_substring(parse);
    if (!substring)
        return FAILURE;
    substring->data = parse->data;
    return NEXT;
}

static State
end_cdata_substring_to_mark(Parse *parse)
{
    DataSize size;

#ifdef DEBUG
    ASSERT(parse->element,
        "Missing element")
    ASSERT(parse->element->parent,
        "Missing element parent")
    ASSERT(parse->element->parent->object,
        "Missing element parent object");
    ASSERT(parse->element->type == AttributeElement,
        "Character data in non-attribute element")
    ASSERT(parse->substrings.list && parse->substrings.last,
        "Missing substring")
#endif

    size = parse->mark - parse->substrings.last->data;
    parse->substrings.last->size = size;
    parse->substrings.size += size;
    return NEXT;
}
