import doctest
from doctest import ELLIPSIS
from doctest import NORMALIZE_WHITESPACE
import linecache

import pytest
from sybil import Sybil
from sybil.parsers.rest import DocTestParser
from sybil.parsers.rest import PythonCodeBlockParser
from sybil.parsers.rest import SkipParser


# --- Make ``inspect.getsource`` work for doctest-defined functions -------
#
# See ``docs/conftest.py`` for an in-depth explanation.  In short, ``doctest``
# compiles every example with a synthetic filename but does not register the
# source with ``linecache``, so ``inspect.getsource`` (used by
# ``audobject.resolver.Function``) raises ``OSError`` for functions defined
# inline in doctests.  We wrap ``DocTestRunner.run`` to register the source.
_orig_doctest_run = doctest.DocTestRunner.run


def _run_with_linecache(self, test, *args, **kwargs):
    counter = getattr(self, "_example_counter", 0) + 1
    self._example_counter = counter
    test.name = f"{test.name}-{counter}"
    for examplenum, example in enumerate(test.examples):
        filename = "<doctest %s[%d]>" % (test.name, examplenum)
        lines = example.source.splitlines(keepends=True)
        linecache.cache[filename] = (len(example.source), None, lines, filename)
    return _orig_doctest_run(self, test, *args, **kwargs)


@pytest.fixture(scope="session")
def _patch_doctest_runner():
    """Install the linecache-aware ``DocTestRunner.run`` for doctests."""
    doctest.DocTestRunner.run = _run_with_linecache
    try:
        yield
    finally:
        doctest.DocTestRunner.run = _orig_doctest_run


# Collect doctests from docstrings in Python source files.
#
# Sybil's default document type for ``*.py`` files is
# ``PythonDocStringDocument``, which:
#
# * extracts only the text of docstrings (so ordinary Python code is ignored),
# * imports the source file as a Python module and populates the doctest
#   namespace with the module's globals.
#
# The latter means classes defined in doctests get the correct ``__module__``
# attribute (e.g. ``audobject.core.object``), matching the expected output
# shown in the docstrings.
pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS | NORMALIZE_WHITESPACE),
        PythonCodeBlockParser(),
        SkipParser(),
    ],
    patterns=["*.py"],
    excludes=["conftest.py"],
    fixtures=["_patch_doctest_runner"],
).pytest()
