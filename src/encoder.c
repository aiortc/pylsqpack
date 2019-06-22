#include <Python.h>
#include "lsqpack.h"

#define ENC_BUF_SZ 4096
#define HDR_BUF_SZ 4096
#define PREFIX_MAX_SIZE 16

typedef struct {
    PyObject_HEAD
    struct lsqpack_enc enc;
    unsigned char hdr_buf[HDR_BUF_SZ];
    unsigned char enc_buf[ENC_BUF_SZ];
    unsigned char pfx_buf[PREFIX_MAX_SIZE];
} EncoderObject;

static int
Encoder_init(EncoderObject *self, PyObject *args, PyObject *kwargs)
{
    lsqpack_enc_preinit(&self->enc, NULL);
    return 0;
}

static void
Encoder_dealloc(EncoderObject *self)
{
    lsqpack_enc_cleanup(&self->enc);
}

static PyObject*
Encoder_encode(EncoderObject *self, PyObject *args)
{
    uint64_t stream_id;
    unsigned seqno;
    PyObject *list, *tuple, *name, *value;
    size_t enc_len, hdr_len, pfx_len;
    size_t enc_off = 0, hdr_off = PREFIX_MAX_SIZE, pfx_off = 0;

    if (!PyArg_ParseTuple(args, "KIO", &stream_id, &seqno, &list))
        return NULL;

    if (!PyList_Check(list)) {
        PyErr_SetString(PyExc_ValueError, "headers must be a list");
        return NULL;
    }

    if (lsqpack_enc_start_header(&self->enc, stream_id, seqno) != 0) {
        PyErr_SetString(PyExc_RuntimeError, "lsqpack_enc_start_header failed");
        return NULL;
    }

    for (Py_ssize_t i = 0; i < PyList_Size(list); ++i) {
        tuple = PyList_GetItem(list, i);
        if (!PyTuple_Check(tuple) || PyTuple_Size(tuple) != 2) {
            PyErr_SetString(PyExc_ValueError, "the header must be a two-tuple");
            return NULL;
        }
        name = PyTuple_GetItem(tuple, 0);
        value = PyTuple_GetItem(tuple, 1);
        if (!PyBytes_Check(name) || !PyBytes_Check(value)) {
            PyErr_SetString(PyExc_ValueError, "the header's name and value must be bytes");
            return NULL;
        }

        enc_len = ENC_BUF_SZ - enc_off;
        hdr_len = HDR_BUF_SZ - hdr_off;
        if (lsqpack_enc_encode(&self->enc,
                               self->enc_buf + enc_off, &enc_len,
                               self->hdr_buf + hdr_off, &hdr_len,
                               PyBytes_AsString(name), PyBytes_Size(name),
                               PyBytes_AsString(value), PyBytes_Size(value),
                               0) != LQES_OK) {
            PyErr_SetString(PyExc_RuntimeError, "lsqpack_enc_encode failed");
            return NULL;
        }
        enc_off += enc_len;
        hdr_off += hdr_len;
    }

    pfx_len = lsqpack_enc_end_header(&self->enc, self->pfx_buf, PREFIX_MAX_SIZE);
    if (pfx_len <= 0) {
        PyErr_SetString(PyExc_RuntimeError, "lsqpack_enc_start_header failed");
        return NULL;
    }
    pfx_off = PREFIX_MAX_SIZE - pfx_len;
    memcpy(self->hdr_buf + pfx_off, self->pfx_buf, pfx_len);

    return PyTuple_Pack(
        2,
        PyBytes_FromStringAndSize((const char*)self->enc_buf, enc_off),
        PyBytes_FromStringAndSize((const char*)self->hdr_buf + pfx_off, hdr_off - pfx_off)
    );
}

static PyObject*
Encoder_feed_control(EncoderObject *self, PyObject *args)
{
    const unsigned char *data = NULL;
    int data_len = 0;

    if (!PyArg_ParseTuple(args, "y#", &data, &data_len))
        return NULL;

    if (lsqpack_enc_decoder_in(&self->enc, data, data_len) < 0) {
        PyErr_SetString(PyExc_RuntimeError, "lsqpack_enc_decoder_in failed");
        return NULL;
    }

    Py_RETURN_NONE;
}

static PyMethodDef Encoder_methods[] = {
    {"encode", (PyCFunction)Encoder_encode, METH_VARARGS, "Encode a list of headers."},
    {"feed_control", (PyCFunction)Encoder_feed_control, METH_VARARGS, "Feed data from the control stream."},
    {NULL}
};

static PyTypeObject EncoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    MODULE_NAME ".Encoder",             /* tp_name */
    sizeof(EncoderObject),              /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)Encoder_dealloc,        /* tp_dealloc */
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
    "QPACK encoder",                    /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    Encoder_methods,                    /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0,                                  /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)Encoder_init,             /* tp_init */
    0,                                  /* tp_alloc */
};
