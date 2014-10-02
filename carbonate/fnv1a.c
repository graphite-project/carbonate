#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "fnv1a.h"

/**
 * Computes the hash position for key in a 16-bit unsigned integer
 * space.  Returns a number between 0 and 65535 based on the FNV1a hash
 * algorithm.
 */
static unsigned short fnv1a_hashpos(const char *key)
{
  unsigned int hash = 2166136261UL;  /* FNV1a */

  for (; *key != '\0'; key++)
    hash = (hash ^ (unsigned int)*key) * 16777619;

  return (unsigned short)((hash >> 16) ^ (hash & (unsigned int)0xFFFF));
}

/*
 * Function to be called from Python
 */
static PyObject* py_fnv1a(PyObject* self, PyObject* args) {
  const char *key;
  
  if (!PyArg_ParseTuple(args, "s", &key)) {
    return NULL;
  }
  // unsigned short int hashpos = 
  return Py_BuildValue("H", fnv1a_hashpos(key));
}

/*
 * Bind Python function names to our C functions
 */
static PyMethodDef fnv1a_methods[] = {
  {"fnv1a", py_fnv1a, METH_VARARGS},
  {NULL, NULL}
};

void initfnv1a(void)
{
PyImport_AddModule("fnv1a");
Py_InitModule("fnv1a", fnv1a_methods);
}
