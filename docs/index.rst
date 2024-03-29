.. include:: ../README.rst

.. toctree::
    :caption: Getting started
    :maxdepth: 2
    :hidden:

    install
    usage

.. Warning: the usage of genindex is a hack to get a TOC entry, see
.. https://stackoverflow.com/a/42310803. This might break the usage of sphinx if
.. you want to create something different than HTML output.
.. toctree::
    :caption: API Documentation
    :hidden:

    api/audobject
    api/audobject.define
    api/audobject.resolver
    api/audobject.testing
    genindex

.. toctree::
    :caption: Development
    :maxdepth: 2
    :hidden:

    contributing
    changelog
