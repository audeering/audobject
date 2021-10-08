Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 0.6.0 (2021-10-08)
--------------------------

* Added: subpackage ``resolver``
* Added:
  ``resolver.FilePath``,
  ``resolver.Function``,
  ``resolver.Tuple``,
  ``resolver.Type``
* Deprecated:
  ``FilePathResolver``,
  ``FunctionResolver``,
  ``TupleResolver``,
  ``TypeResolver``
* Fixed: preserve default arguments in serialized functions
* Fixed: attach source to dynamically created functions


Version 0.5.1 (2021-10-04)
--------------------------

* Added: ``audobject.FunctionResolver``


Version 0.5.0 (2021-09-30)
--------------------------

* Added: ``audobject.from_dict``
* Added: ``audobject.from_yaml``
* Added: ``audobject.from_yaml_s``
* Deprecated: ``audobject.Object.from_dict``
* Deprecated: ``audobject.Object.from_yaml``
* Deprecated: ``audobject.Object.from_yaml_s``


Version 0.4.14 (2021-07-15)
---------------------------

* Added: ``FilePathResolver``


Version 0.4.13 (2021-04-07)
---------------------------

* Fixed: inherit ``borrow``, ``hide`` and ``resolvers``


Version 0.4.12 (2021-03-26)
---------------------------

* Fixed: link "Edit on Github" in documentation
* Fixed: link to ``audfactory.Lookup`` in documentation


Version 0.4.11 (2021-03-24)
---------------------------

* Fixed: remove footer links in documentation


Version 0.4.10 (2021-03-24)
---------------------------

* Changed: add badges to README
* Fixed: updated all links to Github


Version 0.4.9 (2021-03-24)
--------------------------

* Fixed: package metadata defined in ``setup.cfg``


Version 0.4.8 (2021-03-24)
--------------------------

* Changed: move to Github and make open source release


Version 0.4.7 (2021-01-22)
--------------------------

* Changed: ``audobject.Object`` implements ``__hash__()``
* Changed: borrow arguments from dictionary


Version 0.4.6 (2020-12-04)
--------------------------

* Fixed: avoid warnings for unsupported ``kwargs`` in
  ``audobject.Object.from_dict()``

Version 0.4.5 (2020-12-04)
--------------------------

* Added: ``borrow`` argument to ``audobject.init_decorator()``

Version 0.4.4 (2020-12-03)
--------------------------

* Changed: parse authors and project name from setup
* Changed: use ``audeer.deprecated_keyword_argument()``

Version 0.4.3 (2020-11-06)
--------------------------

* Changed: raise error when serializing a callable

Version 0.4.2 (2020-10-23)
--------------------------

* Changed: better error messages
* Changed: ``audobject.init_decorator()`` stores hidden arguments
  before calling ``__init__``

Version 0.4.1 (2020-10-21)
--------------------------

* Added: argument ``flatten`` to ``audobject.Object.to_dict()``

Version 0.4.0 (2020-10-19)
--------------------------

* Added: ``audobject.Object.arguments()``,
  ``audobject.Object.hidden_arguments()``,
  ``audobject.Object.resolvers()``
* Added: ``hide`` to ``audobject.init_decorator()`` (replaces ``ignore_vars``)
* Changed: Serialize only arguments of ``__init__`` to YAML
* Changed: Raise error if user tries to hide argument without default value
* Changed: Raise error if argument that is not hidden is not assigned to a variable
* Removed: ``check_vars`` from ``audobject.init_decorator``

Version 0.3.3 (2020-10-09)
--------------------------

* Fixed: dependency to ``audeer``

Version 0.3.2 (2020-10-08)
--------------------------

* Fixed: support empty dictionary

Version 0.3.1 (2020-10-08)
--------------------------

* Changed: replace ``override_vars`` with ``kwargs``

Version 0.3.0 (2020-10-08)
--------------------------

* Added: option to ignore variables
* Added: option to override variables
* Changed: change ``sanity_check=True`` to ``check_vars=False``

Version 0.2.0 (2020-10-08)
--------------------------

* Added: ``audobject.init_decorator()``
* Added: ``audobject.Dictionary``

Version 0.1.0 (2020-10-02)
--------------------------

* Added: initial release


.. _Keep a Changelog:
    https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning:
    https://semver.org/spec/v2.0.0.html
