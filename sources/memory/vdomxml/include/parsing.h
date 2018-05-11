
/* Substrings */

static Substring *
new_substring(Parse *parse)
{
    Substring *substring = (Substring *)allocate_on_stockpile(&parse->stockpiles.substrings);
    if (!substring)
        return NULL;

    substring->next = NULL;
    if (parse->substrings.list)
        parse->substrings.last->next = substring;
    else
        parse->substrings.list = substring;
    parse->substrings.last = substring;

    return substring;
}

static int
reset_substrings(Parse *parse)
{
#ifdef DEBUG
    if (parse->substrings.list)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unclean substrings");
        return FAILURE;
    }
#endif

    parse->substrings.list = NULL;
    parse->substrings.size = 0;
    return 0;
}

static void
cleanup_substrings(Parse *parse)
{
    release_all_on_stockpile(&parse->stockpiles.substrings);
    parse->substrings.list = NULL;
}


/* Elements */

static Element *
new_element(Parse *parse)
{
    Element *element = (Element *)allocate_on_stockpile(&parse->stockpiles.elements);
    if (!element)
        return NULL;

    element->parent = parse->element;
    element->type = GenericElement;
    element->name = NULL;
    element->attributes = NULL;
    element->object = NULL;

    parse->element = element;
    return element;
}

static void
release_element(Parse *parse)
{
    Element *parent = parse->element->parent;

    Py_XDECREF(parse->element->name);
    parse->element->name = NULL;
    Py_XDECREF(parse->element->attributes);
    parse->element->attributes = NULL;
    Py_XDECREF(parse->element->object);
    parse->element->object = NULL;

    release_one_on_stockpile(&parse->stockpiles.elements);
    parse->element = parent;
}

static int
cleanup_elements_clean(Element *element)
{
    Py_XDECREF(element->name);
    Py_XDECREF(element->attributes);
    Py_XDECREF(element->object);
    return 0;
}

static void
cleanup_elements(Parse *parse)
{
    iterate_stockpile(&parse->stockpiles.elements, (StockpileIterateCallback)cleanup_elements_clean);
    release_all_on_stockpile(&parse->stockpiles.elements);
}


/* Attribute */

static int
reset_attribute(Parse *parse)
{
#ifdef DEBUG
    if (parse->attribute.name)
    {
        PyErr_SetString(PyExc_RuntimeError, "Unclean attribute name");
        return 1;
    }
#endif

    parse->attribute.type = GenericAttribute;
    return 0;
}

static void
cleanup_attribute(Parse *parse)
{
    Py_XDECREF(parse->attribute.name);
    parse->attribute.name = NULL;
}


/* References */

static PyObject **
new_reference(Parse *parse)
{
    PyObject **reference = (PyObject **)allocate_on_stockpile(&parse->stockpiles.references);
    if (!reference)
        return NULL;
    return reference;
}

static int
cleanup_references_clean(PyObject **object)
{
    Py_XDECREF(*object);
    return 0;
}

static void
cleanup_references(Parse *parse)
{
    iterate_stockpile(&parse->stockpiles.references, (StockpileIterateCallback)cleanup_references_clean);
    release_all_on_stockpile(&parse->stockpiles.references);
}
