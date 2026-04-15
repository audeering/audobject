import doctest
from doctest import ELLIPSIS
from doctest import NORMALIZE_WHITESPACE
import linecache
import os
import sys
import types

import pytest
from sybil import Sybil
from sybil.parsers.rest import DocTestParser
from sybil.parsers.rest import PythonCodeBlockParser
from sybil.parsers.rest import SkipParser

import audobject
import audobject.core.utils


# --- Make ``inspect.getsource`` work for doctest-defined functions -------
#
# ``audobject.resolver.Function`` calls ``inspect.getsource(func)`` to
# serialise the source code of a function. ``inspect.getsource`` reads
# source lines from ``linecache`` keyed by ``func.__code__.co_filename``.
#
# Python's ``doctest`` module compiles each example with a synthetic
# filename (``<doctest name[N]>``) but does *not* register the source
# in ``linecache``, so ``inspect.getsource`` raises ``OSError`` for
# functions defined inline in doctests. IPython/Jupyter avoids this by
# registering cell sources in ``linecache`` — we do the same here by
# wrapping ``DocTestRunner.run``.
#
# sybil feeds every example through ``DocTestRunner.run`` as its own
# single-example ``DocTest``, and ``doctest`` builds the filename as
# ``<doctest <test.name>[<examplenum>]>``. If we left ``test.name``
# alone, every example from the same rst file would end up with the
# same filename (``[examplenum]`` is always 0) and each linecache
# entry would overwrite the previous one. We therefore make the name
# unique per example using a monotonic counter.
_orig_doctest_run = doctest.DocTestRunner.run
_example_counter = 0


def _run_with_linecache(self, test, *args, **kwargs):
    global _example_counter
    _example_counter += 1
    test.name = f"{test.name}-{_example_counter}"
    for examplenum, example in enumerate(test.examples):
        filename = "<doctest %s[%d]>" % (test.name, examplenum)
        lines = example.source.splitlines(keepends=True)
        linecache.cache[filename] = (len(example.source), None, lines, filename)
    return _orig_doctest_run(self, test, *args, **kwargs)


doctest.DocTestRunner.run = _run_with_linecache


# --- Fake user package ---------------------------------------------------
#
# audobject stores the class module path and its ``__version__`` in the
# serialised YAML representation of every object.  In the original docs,
# examples were executed in a Jupyter kernel where the classes ended up
# in the ``__main__`` module, and ``__version__ = "X"`` set
# ``__main__.__version__`` which ``audobject.core.utils.get_version``
# could pick up.
#
# Sybil executes doctests via ``exec`` in a plain namespace, so classes
# defined there would otherwise have ``__module__ == "builtins"`` and
# ``__version__`` assignments would not propagate to the module object
# that ``get_version`` inspects.
#
# To preserve the original docs style (``__version__ = "1.0.0"``), we:
#   1) register a fake ``mypkg`` module in ``sys.modules`` and make the
#      doctest namespace pretend ``__name__ == "mypkg"`` so classes
#      defined there get ``__module__ == "mypkg"``;
#   2) patch ``audobject.core.utils.get_version`` so that when asked for
#      ``mypkg``'s version it returns the current ``__version__`` from
#      the live doctest namespace.
_doctest_namespace: dict = {}


class _MyPkgModule(types.ModuleType):
    """Fake ``mypkg`` module backed by the live doctest namespace.

    Classes defined in the doctest namespace are looked up here via
    ``__getattr__`` so that ``audobject`` can re-instantiate them when
    deserialising YAML.
    """

    def __getattr__(self, name):
        if name in _doctest_namespace:
            return _doctest_namespace[name]
        raise AttributeError(name)


_mypkg = _MyPkgModule("mypkg")
sys.modules["mypkg"] = _mypkg

_orig_get_version = audobject.core.utils.get_version


def _patched_get_version(module_name):
    root = module_name.split(".")[0]
    if root == "mypkg" and "__version__" in _doctest_namespace:
        return _doctest_namespace["__version__"]
    return _orig_get_version(module_name)


# ``get_version`` inspects ``module.__dict__`` directly, bypassing our
# module ``__getattr__``, so we patch it to read from the live doctest
# namespace whenever ``mypkg`` is queried.
audobject.core.utils.get_version = _patched_get_version


def imports(namespace):
    """Provide modules to the doctest namespace."""
    global _doctest_namespace
    # Make classes defined here end up in the fake ``mypkg`` module.
    namespace["__name__"] = "mypkg"
    namespace["__version__"] = "1.0.0"
    namespace["audobject"] = audobject
    # Bind the live namespace so ``_patched_get_version`` and the fake
    # ``mypkg`` module can look up ``__version__`` and classes as they
    # are defined during doctest execution.
    _doctest_namespace = namespace


@pytest.fixture(scope="module")
def run_in_tmpdir(tmpdir_factory):
    """Move to a persistent tmpdir for execution of a whole file."""
    tmpdir = tmpdir_factory.mktemp("tmp")
    current_dir = os.getcwd()
    os.chdir(tmpdir)

    yield

    os.chdir(current_dir)


# Collect doctests
pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS | NORMALIZE_WHITESPACE),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=["usage.rst"],
    fixtures=["run_in_tmpdir"],
    setup=imports,
).pytest()
