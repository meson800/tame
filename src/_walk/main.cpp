#include <filesystem>
#include <string>
#include <vector>

#define PY_SSIZE_T_CLEAN
#include <Python.h>

static PyObject* walk(PyObject *self, PyObject *args)
{
    const char* walk_start;
    PyObject* input_args;
    if (!PyArg_ParseTuple(args, "sO", &walk_start, &input_args))
    {
        return nullptr;
    }

    std::vector<std::string> extensions;
    // Check if object is a string
    if (PyUnicode_Check(input_args)) 
    {
        const char* extension = PyUnicode_AsUTF8(input_args);
        if (extension == nullptr)
        {
            return nullptr;
        }
        extensions.emplace_back(extension);
    } else if (PyList_Check(input_args)) {
        Py_ssize_t len = PyList_Size(input_args);
        for (Py_ssize_t i = 0; i < len; ++i)
        {
            PyObject* str = PyList_GetItem(input_args, i);
            if (str == nullptr)
            {
                return nullptr;
            }

            if (!PyUnicode_Check(str)) 
            {
                // List element is not a string.
                PyErr_SetString(PyExc_TypeError, "Extensions must"
                        " be based as a list of strings!");
                return nullptr;
            }

            const char* extension = PyUnicode_AsUTF8(str);
            if (extension == nullptr)
            {
                return nullptr;
            }
            extensions.emplace_back(extension);
        }
    } else {
        // Unexpected argument
        PyErr_SetString(PyExc_TypeError, "Extensions must"
                " be specified as a single string or a list of strings!");
        return nullptr;
    }


    // At this point, we have a list of std::strings in extensions to match against.
    PyObject* list = PyList_New(0);
    if (list == nullptr)
    {
        return nullptr;
    }
    try
    {
        for (auto& p : std::filesystem::recursive_directory_iterator(walk_start))
        {
            bool valid = false;
            std::filesystem::path path = p.path();
            for (std::string const& extension : extensions)
            {
                valid |= (path.extension().string() == extension);
            }
            if (valid)
            {
                PyObject* value = Py_BuildValue("s", path.string().c_str());
                if (value == nullptr)
                {
                    return nullptr;
                }

                if (PyList_Append(list, value) != 0)
                {
                    return nullptr;
                }
            }
        }
    } catch (const std::exception& ex) {
        PyErr_SetString(PyExc_RuntimeError, ex.what());
        return nullptr;
    } catch (...) {
        PyErr_SetString(PyExc_RuntimeError, "Unspecified C++ runtime error");
        return nullptr;
    }
    return list;
}

static PyMethodDef WalkMethods[] = {
    {"walk", walk, METH_VARARGS, "Test."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef walkmodule = {
    PyModuleDef_HEAD_INIT,
    "_tame_walk",
    NULL,
    -1,
    WalkMethods
};


PyMODINIT_FUNC
PyInit__tame_walk(void)
{
    return PyModule_Create(&walkmodule);
}
