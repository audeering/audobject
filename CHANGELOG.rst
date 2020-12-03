Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.


Version 0.4.4 (2020-12-03)
--------------------------

* Changed: parse authors and project name from setup
* Changed: use :func:`audeer.deprecated_keyword_argument`

Version 0.4.3 (2020-11-06)
--------------------------

* Changed: raise error when serializing a callable

Version 0.4.2 (2020-10-23)
--------------------------

* Changed: better error messages
* Changed: :meth:`audobject.init_decorator` stores hidden arguments before calling ``__init__``

Version 0.4.1 (2020-10-21)
--------------------------

* Added: argument ``flatten`` to :meth:`audobject.Object.to_dict`

Version 0.4.0 (2020-10-19)
--------------------------

* Added: :meth:`audobject.Object.arguments`, :meth:`audobject.Object.hidden_arguments`, :meth:`audobject.Object.resolvers`
* Added: ``hide`` to :meth:`audobject.init_decorator` (replaces ``ignore_vars``)
* Changed: Serialize only arguments of __init__ to YAML
* Changed: Raise error if user tries to hide argument without default value
* Changed: Raise error if argument that is not hidden is not assigned to a variable
* Removed: ``check_vars`` from :meth:`audobject.init_decorator`

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

* Added: :meth:`audobject.init_decorator`
* Added: :class:`audobject.Dictionary`

Version 0.1.0 (2020-10-02)
--------------------------

* Added: initial release


.. _Keep a Changelog:
    https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning:
    https://semver.org/spec/v2.0.0.html
