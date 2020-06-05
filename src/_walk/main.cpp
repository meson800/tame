#include <filesystem>
#include <string>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* walk(PyObject *self, PyObject *args)
{
    const char* filename;
    if (!PyArg_ParseTuple(args, "s", &filename))
    {
        return NULL;
    }

    std::string target{".yaml"};

    PyObject* list = PyList_New(0);
    for (auto& p : std::filesystem::recursive_directory_iterator(filename))
    {
        std::filesystem::path path = p.path();
        if (path.extension().string() == target)
        {
            PyObject* value = Py_BuildValue("s", path.string().c_str());
            PyList_Append(list, value);
        }
    }
    return list;
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
