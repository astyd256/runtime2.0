
#define IS_HIGH_SURROGATE(value) (0xD800 <= value && value <= 0xDBFF)
#define IS_LOW_SURROGATE(value) (0xDC00 <= value && value <= 0xDFFF)

#define JOIN_SURROGATES(high, low) \
    (0x10000 + ((((Character)(high) & 0x03FF) << 10) | ((Character)(low) & 0x03FF)))


#define STRING_NEXT(data, stop) (Character)(*((unsigned char *)(data))++)

#ifdef Py_UNICODE_WIDE
#   define UNICODE_NEXT(data, stop) (Character)(*((Py_UNICODE *)(data))++)
#else
#   define UNICODE_NEXT(data, stop) \
        (((IS_HIGH_SURROGATE(*((Py_UNICODE *)(data))) \
            && (data) < (stop) \
            && IS_LOW_SURROGATE(((Py_UNICODE *)(data))[1]))) \
        ? (((Py_UNICODE *)(data)) += 2, \
            JOIN_SURROGATES(((Py_UNICODE *)(data))[-2], ((Py_UNICODE *)(data))[-1])) \
        : (Character)(*((Py_UNICODE *)(data))++))
#endif


static int
string_match_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || tolower(*data++) != *value++)
            return 0;
    };
};

static int
unicode_match_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || tolower(*((Py_UNICODE *)data)++) != *value++)
            return 0;
    };
};


static int
string_is_equal_to_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || *data++ != *value++)
            return 0;
    };
};

static int
unicode_is_equal_to_string(Data data, Data stop, char *value)
{
    for (;;)
    {
        if (*value == '\0')
            return data == stop;
        if (data == stop || *((Py_UNICODE *)data)++ != *value++)
            return 0;
    };
};


static int
string_is_equal_to_python_string(Data data, Data stop, PyObject *object)
{
    Data object_data = (char *)PyString_AS_STRING(object);
    DataSize object_size = PyString_GET_SIZE(object);
    return ((stop - data) == object_size) && !memcmp(data, object_data, object_size);
};

static int
unicode_is_equal_to_python_string(Data data, Data stop, PyObject *object)
{
    Data object_data = (char *)PyUnicode_AS_DATA(object);
    DataSize object_size = PyUnicode_GET_DATA_SIZE(object);
    return ((stop - data) == object_size) && !memcmp(data, object_data, object_size);
};


static int
string_python_string_is_equal_to_string(PyObject *object, char *value)
{
    Data data = (Data)PyString_AS_STRING(object);
    DataSize size = PyString_GET_SIZE(object);
    return string_is_equal_to_string(data, data + size, value);
};

static int
unicode_python_string_is_equal_to_string(PyObject *object, char *value)
{
    Data data = (Data)PyUnicode_AS_DATA(object);
    DataSize size = PyUnicode_GET_DATA_SIZE(object);
    return unicode_is_equal_to_string(data, data + size, value);
};


static PyObject *
string_create_python_string(Data data, Data stop)
{
    return PyString_FromStringAndSize((char *)data, stop - data);
}

static PyObject *
unicode_create_python_string(Data data, Data stop)
{
    Length length = (stop - data) / Py_UNICODE_SIZE;
#ifdef DEBUG
    if ((stop - data) % Py_UNICODE_SIZE)
    {
        PyErr_SetString(PyExc_RuntimeError, "Inconsistency in internal buffers");
        return NULL;
    }
#endif
    return PyUnicode_FromUnicode((Py_UNICODE *)data, length);
}


static PyObject *
string_create_python_string_from_substrings(Substrings *substrings)
{
    PyObject *object;
    Substring *substring;
    Data data;

    object = PyString_FromStringAndSize(NULL, substrings->size);
    if (!object)
        return NULL;

    data = PyString_AS_STRING(object);
    for (substring = substrings->list; substring; substring = substring->next)
    {
        Py_MEMCPY(data, substring->data, substring->size);
        data += substring->size;
    }

    return object;
}

static PyObject *
unicode_create_python_string_from_substrings(Substrings *substrings)
{
    DataSize length;
    PyObject *object;
    Substring *substring;
    Data data;

    length = substrings->size / Py_UNICODE_SIZE;
#ifdef DEBUG
    if (substrings->size % Py_UNICODE_SIZE)
    {
        PyErr_SetString(PyExc_RuntimeError, "Inconsistency in internal buffers");
        return NULL;
    }
#endif

    object = PyUnicode_FromUnicode(NULL, length);
    if (!object)
        return NULL;

    data = (char *)PyUnicode_AS_DATA(object);
    for (substring = substrings->list; substring; substring = substring->next)
    {
        Py_MEMCPY(data, substring->data, substring->size);
        data += substring->size;
    }

    return object;
}


static PyObject *
string_create_empty_python_string()
{
    return Py_BuildValue("s", "");
}

static PyObject *
unicode_create_empty_python_string()
{
    return Py_BuildValue("u", "");
}


static DataSize
string_write_character(Data data, Character character)
{
    if (character > 0x7F)
    {
        PyErr_Format(WrongCharacterError, "Wrong character '?' (0x%x)", character);
        return 0;
    }

    *((char *)data) = (char)character;
    return 1;
}

static DataSize
unicode_write_character(Data data, Character character)
{
    if (character > 0x7F)
    {
        PyErr_Format(WrongCharacterError, "Wrong character '?' (0x%x)", character);
        return 0;
    }

    *((Py_UNICODE *)data) = (Py_UNICODE)character;
    return Py_UNICODE_SIZE;
}
