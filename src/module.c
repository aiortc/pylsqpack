#include <Python.h>
#include "lsqpack.h"

#define MODULE_NAME "pylsqpack"

#include "decoder.c"
#include "encoder.c"

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    MODULE_NAME,                        /* m_name */
    "Bindings for ls-qpack.",           /* m_doc */
    -1,                                 /* m_size */
    NULL,                               /* m_methods */
    NULL,                               /* m_reload */
    NULL,                               /* m_traverse */
    NULL,                               /* m_clear */
    NULL,                               /* m_free */
};

PyMODINIT_FUNC
PyInit_pylsqpack(void)
{
    PyObject* m;

    m = PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    DecoderType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&DecoderType) < 0)
        return NULL;
    Py_INCREF(&DecoderType);
    PyModule_AddObject(m, "Decoder", (PyObject *)&DecoderType);

    EncoderType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&EncoderType) < 0)
        return NULL;
    Py_INCREF(&EncoderType);
    PyModule_AddObject(m, "Encoder", (PyObject *)&EncoderType);

    return m;
}
