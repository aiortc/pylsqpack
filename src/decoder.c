#include <Python.h>
#include "lsqpack.h"

#define DEC_BUF_SZ 4096

typedef struct {
    PyObject_HEAD
    struct lsqpack_dec dec;
    unsigned char dec_buf[DEC_BUF_SZ];
} DecoderObject;

static int
Decoder_init(DecoderObject *self, PyObject *args, PyObject *kwargs)
{
    char *kwlist[] = {"dyn_table_size", "max_risked_streams", NULL};
    unsigned dyn_table_size, max_risked_streams;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "II", kwlist, &dyn_table_size, &max_risked_streams))
        return -1;

    lsqpack_dec_init(&self->dec, NULL, dyn_table_size, max_risked_streams, NULL);
    return 0;
}

static void
Decoder_dealloc(DecoderObject *self)
{
    lsqpack_dec_cleanup(&self->dec);
}

static PyObject*
Decoder_feed_control(DecoderObject *self, PyObject *args)
{
    const unsigned char *data = NULL;
    int data_len = 0;

    if (!PyArg_ParseTuple(args, "y#", &data, &data_len))
        return NULL;

    if (lsqpack_dec_enc_in(&self->dec, data, data_len) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to feed control to decoder");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyObject*
Decoder_feed_header(DecoderObject *self, PyObject *args)
{
    uint64_t stream_id;
    const unsigned char *data = NULL;
    int data_len = 0;
    struct lsqpack_header_set *hset;
    struct lsqpack_header *header;
    PyObject *list, *tuple, *name, *value;
    size_t dec_len = DEC_BUF_SZ;

    if (!PyArg_ParseTuple(args, "Ky#", &stream_id, &data, &data_len))
        return NULL;

    if (lsqpack_dec_header_in(&self->dec, NULL, stream_id, data_len, &data, data_len, &hset, self->dec_buf, &dec_len) != LQRHS_DONE) {
        PyErr_SetString(PyExc_RuntimeError, "lsqpack_dec_header_in failed");
        return NULL;
    }

    list = PyList_New(hset->qhs_count);
    for (size_t i = 0; i < hset->qhs_count; ++i) {
        header = hset->qhs_headers[i];
        name = PyBytes_FromStringAndSize(header->qh_name, header->qh_name_len);
        value = PyBytes_FromStringAndSize(header->qh_value, header->qh_value_len);
        tuple = PyTuple_Pack(2, name, value);
        Py_DECREF(name);
        Py_DECREF(value);
        PyList_SET_ITEM(list, i, tuple);
    }
    lsqpack_dec_destroy_header_set(hset);

    return PyTuple_Pack(
        2,
        PyBytes_FromStringAndSize((const char*)self->dec_buf, dec_len),
        list
    );
}

static PyMethodDef Decoder_methods[] = {
    {"feed_control", (PyCFunction)Decoder_feed_control, METH_VARARGS, "Feed data from the control stream."},
    {"feed_header", (PyCFunction)Decoder_feed_header, METH_VARARGS, "Feed data from a data stream."},
    {NULL}
};

static PyTypeObject DecoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    MODULE_NAME ".Decoder",             /* tp_name */
    sizeof(DecoderObject),              /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)Decoder_dealloc,        /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_reserved */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash  */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    "QPACK decoder",                    /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    Decoder_methods,                    /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)Decoder_init,             /* tp_init */
    0,                                  /* tp_alloc */
};
