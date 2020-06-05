#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* walk(PyObject *self, PyObject *args)
{
    return PyLong_FromLong(1);
}

static PyMethodDef WalkMethods[] = {
    {"walk", walk, METH_VARARGS, "Test."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef walkmodule = {
    PyModuleDef_HEAD_INIT,
    "_walk",
    NULL,
    -1,
    WalkMethods
};


PyMODINIT_FUNC
PyInit__walk(void)
{
    return PyModule_Create(&walkmodule);
}
