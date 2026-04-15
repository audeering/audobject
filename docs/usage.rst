Usage
=====

The aim of :mod:`audobject` is to provide
a base class, namely :class:`audobject.Object`,
which allows it to convert an object to a YAML string
and re-instantiate the object from it.


Object class
------------

Let's create a class that derives from :class:`audobject.Object`.

.. code-block:: python

    __version__ = "1.0.0"  # pretend we have a package version

    class MyObject(audobject.Object):

        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return " ".join([self.string] * self.num_repeat)

Now we instantiate an object and print it.

.. code-block:: pycon

    >>> o = MyObject("hello object!", num_repeat=2)
    >>> print(o)
    hello object! hello object!

As expected we see that ``string`` is repeated ``num_repeat`` times.
But since we derived from :class:`audobject.Object`
we get some additional functionality.

For instance, we can get a dictionary
with the arguments the object was initialized with.

.. code-block:: pycon

    >>> o.arguments
    {'string': 'hello object!', 'num_repeat': 2}

Or a dictionary that also stores module,
object name and package version.

.. code-block:: pycon

    >>> o_dict = o.to_dict()
    >>> print(o_dict)
    {'$mypkg.MyObject==1.0.0': {'string': 'hello object!', 'num_repeat': 2}}

And we can re-instantiate the object from it.

.. code-block:: pycon

    >>> o2 = audobject.from_dict(o_dict)
    >>> print(o2)
    hello object! hello object!

We can also convert it to YAML.

.. code-block:: pycon

    >>> o_yaml = o.to_yaml_s()
    >>> print(o_yaml)
    $mypkg.MyObject==1.0.0:
      string: hello object!
      num_repeat: 2
    <BLANKLINE>

And create the object from YAML.

.. code-block:: pycon

    >>> o3 = audobject.from_yaml_s(o_yaml)
    >>> print(o3)
    hello object! hello object!

If we want, we can override
arguments when we instantiate an object.

.. code-block:: pycon

    >>> o4 = audobject.from_yaml_s(
    ...     o_yaml,
    ...     override_args={
    ...         "string": "I was set to a different value!"
    ...     }
    ... )
    >>> print(o4)
    I was set to a different value! I was set to a different value!

Or save an object to disk and re-instantiate it from there.

.. code-block:: pycon

    >>> file = "my.yaml"
    >>> o.to_yaml(file)
    >>> o5 = audobject.from_yaml(file)
    >>> print(o5)
    hello object! hello object!

Object ID
---------

Every object has an ID.

.. code-block:: pycon

    >>> o = MyObject("I am unique!", num_repeat=2)
    >>> print(o.id)
    9268115e-7caf-aa02-7fbb-da4e83b2f575

Objects with exact same arguments share the same ID.

.. code-block:: pycon

    >>> o2 = MyObject("I am unique!", num_repeat=2)
    >>> print(o.id == o2.id)
    True

When an object is serialized the ID does not change.

.. code-block:: pycon

    >>> o3 = audobject.from_yaml_s(o.to_yaml_s())
    >>> print(o3.id == o.id)
    True

Objects with different arguments get different IDs.

.. code-block:: pycon

    >>> o4 = MyObject("I am different!", num_repeat=2)
    >>> print(o.id == o4.id)
    False

Malformed objects
-----------------

In the constructor of ``MyObject`` we have assigned
every argument to an attribute with the same name.
This ensures that we can re-instantiate the object from YAML.
Let's create a class where we don't follow this rule.

.. code-block:: python

    class MyBadObject(audobject.Object):

        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
        ):
            self.msg = string
            self.repeat = num_repeat

        def __str__(self) -> str:
            return " ".join([self.msg] * self.repeat)

At a first glance, everything works as expected.

.. code-block:: pycon

    >>> bad = MyBadObject("test", num_repeat=2)
    >>> print(bad)
    test test

But if we try to serialize the object to YAML,
we'll get an error.

.. code-block:: pycon

    >>> bad.to_yaml_s()
    Traceback (most recent call last):
        ...
    RuntimeError: Arguments ['string', 'num_repeat'] of <class 'mypkg.MyBadObject'> not assigned to attributes of same name.

However, in the next section we'll learn
that it's possible to hide arguments.
If we hide an argument, we don't have to set
it to an attribute of the same name.

Hidden arguments
----------------

Hidden arguments are arguments that are not serialized.

.. note:: Only arguments with a default value can be hidden.

Let's introduce a new argument ``verbose`` and hide it
with the :meth:`audobject.init_decorator` decorator.

.. code-block:: python

    class MyObjectWithHiddenArgument(audobject.Object):

        @audobject.init_decorator(
            hide=["verbose"],
        )
        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
                verbose: bool = False,
        ):
            self.string = string
            self.num_repeat = num_repeat
            self.debug = verbose  # "verbose" is hidden, so we can set it to a different name

        def __str__(self) -> str:
            if self.debug:
                print("LOG: print message")
            return " ".join([self.string] * self.num_repeat)

If we set ``verbose=True``, debug message are printed.

.. code-block:: pycon

    >>> o = MyObjectWithHiddenArgument(
    ...     "hello object!",
    ...     num_repeat=3,
    ...     verbose=True,
    ... )
    >>> print(o)
    LOG: print message
    hello object! hello object! hello object!

But since ``verbose`` is a hidden argument,
it is not stored to YAML.

.. code-block:: pycon

    >>> o_yaml = o.to_yaml_s()
    >>> print(o_yaml)
    $mypkg.MyObjectWithHiddenArgument==1.0.0:
      string: hello object!
      num_repeat: 3
    <BLANKLINE>

That means when we re-instantiate the object,
``verbose`` will be set to its default value (``False``)
and we won't see debug messages.

.. code-block:: pycon

    >>> o2 = audobject.from_yaml_s(o_yaml)
    >>> print(o2)
    hello object! hello object! hello object!

However, we can still set ``verbose``
to ``True`` when we load the object.

.. code-block:: pycon

    >>> o3 = audobject.from_yaml_s(
    ...     o_yaml,
    ...     override_args={
    ...         "verbose": True,
    ...     }
    ... )
    >>> print(o3)
    LOG: print message
    hello object! hello object! hello object!

Note that hidden arguments are not taken into account for the UID.

.. code-block:: pycon

    >>> print(o2.id)
    26eddeb8-2ead-69e1-0eb2-37c2a2d19174
    >>> print(o3.id)
    26eddeb8-2ead-69e1-0eb2-37c2a2d19174

It is possible to get a list of hidden arguments.

.. code-block:: pycon

    >>> o3.hidden_arguments
    ['verbose']

Borrowed arguments
------------------

It is possible to borrow arguments from an instance attribute.
For instance, here we borrow the attributes ``x``, ``y``, and ``z``
from ``self.point`` and a dictionary ``self.d``.
Using borrowed arguments it becomes possible
to add properties with the name of an argument.

.. code-block:: python

    class Point:

        def __init__(
                self,
                x: int,
                y: int,
        ):
            self.x = x
            self.y = y


    class ObjectWithBorrowedArguments(audobject.Object):

        @audobject.init_decorator(
            borrow={
                "x": "point",
                "y": "point",
                "z": "d",
            },
        )
        def __init__(
                self,
                x: int,
                y: int,
                z: int,
        ):
            self.point = Point(x, y)
            self.d = {"z": z}

        @property
        def z(self):  # property sharing the name of an argument
            return self.d["z"]

.. code-block:: pycon

    >>> o = ObjectWithBorrowedArguments(0, 1, 2)
    >>> print(o.to_yaml_s())
    $mypkg.ObjectWithBorrowedArguments==1.0.0:
      x: 0
      y: 1
      z: 2
    <BLANKLINE>

Object with kwargs
------------------

If the ``__init__`` function accepts ``**kwargs``,
we have to pass them to the base class.
This is necessary,
since we cannot figure out
the names of additional keyword arguments
from the signature of the function.

.. code-block:: python

    class MyObjectWithKwargs(audobject.Object):

        def __init__(
                self,
                string: str,
                **kwargs,
        ):
            super().__init__(**kwargs)  # inform base class about keyword arguments

            self.string = string
            self.num_repeat = kwargs["num_repeat"] if "num_repeat" in kwargs else 1

        def __str__(self) -> str:
            return " ".join([self.string] * self.num_repeat)

.. code-block:: pycon

    >>> o = MyObjectWithKwargs("I have kwargs", num_repeat=3)
    >>> print(o)
    I have kwargs I have kwargs I have kwargs

When we serialize the object,
we see that keyword argument
``num_repeat`` will be included.

.. code-block:: pycon

    >>> o_yaml = o.to_yaml_s()
    >>> print(o_yaml)
    $mypkg.MyObjectWithKwargs==1.0.0:
      string: I have kwargs
      num_repeat: 3
    <BLANKLINE>

Object as argument
------------------

It is possible to have arguments of
type :class:`audobject.Object`.
For instance, we can define the following class.

.. code-block:: python

    class MySuperObject(audobject.Object):

        def __init__(
                self,
                obj: MyObject,
        ):
            self.obj = obj

        def __str__(self) -> str:
            return f"[{str(self.obj)}]"

And initialize it with an instance of ``MyObject``.

.. code-block:: pycon

    >>> o = MyObject("eat me!")
    >>> w = MySuperObject(o)
    >>> print(w)
    [eat me!]

This translates to the following YAML string.

.. code-block:: pycon

    >>> w_yaml = w.to_yaml_s()
    >>> print(w_yaml)
    $mypkg.MySuperObject==1.0.0:
      obj:
        $mypkg.MyObject==1.0.0:
          string: eat me!
          num_repeat: 1
    <BLANKLINE>

From which we can re-instantiate the object.

.. code-block:: pycon

    >>> w2 = audobject.from_yaml_s(w_yaml)
    >>> print(w2)
    [eat me!]

Value resolver
--------------

As long as the type of an arguments is one of:

* ``bool``
* ``datetime.datetime``
* ``dict``
* ``float``
* ``int``
* ``list``
* ``None``
* ``Object``
* ``str``

it is ensured that we get a clean YAML file.

Other types may be encoded using the ``!!python/object`` tag
and clutter the YAML syntax.

To illustrate this, let's use an instance of timedelta_.

.. code-block:: python

    from datetime import timedelta


    class MyDeltaObject(audobject.Object):

        def __init__(
                self,
                delta: timedelta,
        ):
            self.delta = delta

        def __str__(self) -> str:
            return str(self.delta)

As before, we can create an instance and print it.

.. code-block:: pycon

    >>> delta = timedelta(
    ...     days=50,
    ...     seconds=27,
    ...     microseconds=10,
    ...     milliseconds=29000,
    ...     minutes=5,
    ...     hours=8,
    ...     weeks=2
    ... )
    >>> d = MyDeltaObject(delta)
    >>> print(d)
    64 days, 8:05:56.000010

But if we convert it to YAML,
we'll see a warning.

.. skip: next

.. code-block:: python

    d_yaml = d.to_yaml_s()
    print(d_yaml)

And in fact, we can see that
the ``delta`` value is encoded
with a ``!!python/object`` tag,
which is followed by some plain numbers.
Only after looking into the documentation of
timedelta_ we can guess that
they probably encode ``days``, ``seconds``,
and ``microseconds``.

We can avoid this by providing a custom resolver
that defines how a timedelta_ object should be
encoded and decoded.

.. code-block:: python

    class DeltaResolver(audobject.resolver.Base):

        def decode(self, value: dict) -> timedelta:
            return timedelta(
                days=value["days"],
                seconds=value["seconds"],
                microseconds=value["microseconds"],
            )

        def encode(self, value: timedelta) -> dict:
            return {
                "days": value.days,
                "seconds": value.seconds,
                "microseconds": value.microseconds,
            }

        def encode_type(self):
            return dict

To apply our custom resolver to the
``delta`` argument, we pass it to the
:meth:`audobject.init_decorator`
decorator of the ``__init__`` function.

.. code-block:: python

    class MyResolvedDeltaObject(audobject.Object):

        @audobject.init_decorator(
            resolvers={"delta": DeltaResolver},
        )
        def __init__(
                self,
                delta: timedelta,
        ):
            self.delta = delta

        def __str__(self) -> str:
            return str(self.delta)

Now, we don't get a warning
and the ``!!python/object`` tag has disappeared.

.. code-block:: pycon

    >>> d = MyResolvedDeltaObject(delta)
    >>> d_yaml = d.to_yaml_s()
    >>> print(d_yaml)
    $mypkg.MyResolvedDeltaObject==1.0.0:
      delta:
        days: 64
        seconds: 29156
        microseconds: 10
    <BLANKLINE>

Resolve file paths
------------------

Portability is a core feature of
:mod:`audobject`.
Assume we have an object
that takes as argument the path to a file.
When we serialize the object
we want to make sure that:

1. we store the file path relative to the YAML file
2. the path is correctly expanded when we re-instantiate the object

This can be achieved using
:class:`audobject.resolver.FilePath`.

.. code-block:: python

    class MyObjectWithFile(audobject.Object):

        @audobject.init_decorator(
            resolvers={
                "path": audobject.resolver.FilePath,  # ensure portability
            }
        )
        def __init__(
                self,
                path: str,
        ):
            self.path = path

        def read(self):  # print path and content
            print(self.path)
            with open(self.path, "r") as fp:
                print(fp.readlines())

Here, we create a file and pass it to the object.

.. code-block:: pycon

    >>> import os
    >>> import audeer
    >>> root = "root"
    >>> res_path = os.path.join(root, "re", "source.txt")  # root/re/source.txt
    >>> _ = audeer.mkdir(os.path.dirname(res_path))
    >>> with open(res_path, "w") as fp:
    ...     _ = fp.write("You found me!")
    >>> o = MyObjectWithFile(res_path)
    >>> o.read()
    root/re/source.txt
    ['You found me!']

When we serialize the object,
the path is
stored relative to the directory
of the YAML file.

.. code-block:: pycon

    >>> import yaml
    >>> yaml_path = os.path.join(root, "yaml", "object.yaml")  # root/yaml/object.yaml
    >>> o.to_yaml(yaml_path)
    >>> with open(yaml_path, "r") as fp:
    ...     content = yaml.load(fp, Loader=yaml.Loader)
    >>> content
    {'$mypkg.MyObjectWithFile==1.0.0': {'path': '../re/source.txt'}}

When we re-instantiate the object
the path gets expanded again.

.. code-block:: pycon

    >>> o2 = audobject.from_yaml(yaml_path)
    >>> print(o2.path.endswith(os.path.join("root", "re", "source.txt")))
    True
    >>> with open(o2.path, "r") as fp:
    ...     fp.readlines()
    ['You found me!']

This will also work from another location.
Note that we have to move all referenced files as well,
as their relative location to the YAML file must not change.

.. code-block:: pycon

    >>> import shutil
    >>> new_root = os.path.join("some", "where", "else")
    >>> _ = shutil.move(root, new_root)
    >>> yaml_path_new = os.path.join(new_root, "yaml", "object.yaml")
    >>> o3 = audobject.from_yaml(yaml_path_new)
    >>> print(o3.path.endswith(os.path.join("else", "re", "source.txt")))
    True
    >>> with open(o3.path, "r") as fp:
    ...     fp.readlines()
    ['You found me!']


Serialize functions
-------------------

To serialize functions,
a special resolver
:class:`audobject.resolver.Function`
can be used.
It encodes the source code of the function
and dynamically creates the function during decoding.

.. note::
    The examples in this section require function source code
    to be stored in a real ``.py`` file,
    so they are not executed as doctests here.

.. skip: start

The following class takes as arguments a function with two parameters.

.. code-block:: python

    from collections.abc import Callable


    class MyObjectWithFunction(audobject.Object):

        @audobject.init_decorator(
            resolvers={
                "func": audobject.resolver.Function,
            }
        )
        def __init__(
                self,
                func: Callable[[int, int], int],
        ):
            self.func = func

        def __call__(self, a: int, b: int):
            return self.func(a, b)

Here, we initialize an object with a function that sums up the two parameters.

.. code-block:: python

    def add(a, b):
        return a + b


    o = MyObjectWithFunction(add)
    o(1, 2)

When we serialize the object,
the definition of our function is stored in plain text.

.. code-block:: python

    o_yaml = o.to_yaml_s()
    print(o_yaml)

From which the function can be dynamically initialized
when the object is recreated.

.. code-block:: python

    o2 = audobject.from_yaml_s(o_yaml)
    o2(2, 3)

It also works for lambda expressions.

.. code-block:: python

    o3 = MyObjectWithFunction(lambda a, b: a * b)

    o3_yaml = o3.to_yaml_s()
    print(o3_yaml)

.. code-block:: python

    o4 = audobject.from_yaml_s(o3_yaml)
    o4(2, 3)

Instead of a function,
we can also pass a callable object
that derives from
:class:`audobject.Object`.

.. code-block:: python

    class MyCallableObject(audobject.Object):

        def __init__(
            self,
            n: int,
        ):
            self.n = n

        def __call__(self, a: int, b: int):
            return (a + b) * self.n


    a_callable_object = MyCallableObject(2)
    o5 = MyObjectWithFunction(a_callable_object)
    o5(4, 5)

In that case,
the YAML representation is store
instead of the function code.

.. code-block:: python

    o5_yaml = o5.to_yaml_s()
    print(o5_yaml)

And we can still restore the original object.

.. code-block:: python

    o6 = audobject.from_yaml_s(o5_yaml)
    o6(4, 5)

.. skip: end

.. warning:: Since the described mechanism
    offers a way to execute arbitrary Python code,
    you should never load objects from a source you do not trust!


Flat dictionary
---------------

Let's create a class that takes
as input a string, a list and a dictionary.

.. code-block:: python

    class MyListDictObject(audobject.Object):

        def __init__(
                self,
                a_str: str,
                a_list: list,
                a_dict: dict,
        ):
            self.a_str = a_str
            self.a_list = a_list
            self.a_dict = a_dict

And initialize an object.

.. code-block:: pycon

    >>> inner = MyObject("hello")
    >>> o = MyListDictObject(
    ...     a_str="test",
    ...     a_list=[1, "2", inner],
    ...     a_dict={"pi": 3.1416, "e": 2.71828},
    ... )
    >>> import pprint
    >>> pprint.pprint(o.to_dict())
    {'$mypkg.MyListDictObject==1.0.0': {'a_dict': {'e': 2.71828, 'pi': 3.1416},
                                        'a_list': [1,
                                                   '2',
                                                   {'$mypkg.MyObject==1.0.0': {'num_repeat': 1,
                                                                               'string': 'hello'}}],
                                        'a_str': 'test'}}

As expected, the dictionary of the object
looks pretty nested.
This is not always handy,
e.g. if we try to store the object to a lookup table,
this would not work.
Therefore, in can sometimes be useful to
get a flatten version of the dictionary.

.. code-block:: pycon

    >>> pprint.pprint(o.to_dict(flatten=True))
    {'a_dict.e': 2.71828,
     'a_dict.pi': 3.1416,
     'a_list.0': 1,
     'a_list.1': '2',
     'a_list.2.num_repeat': 1,
     'a_list.2.string': 'hello',
     'a_str': 'test'}

However, it's important to note that it's not possible
to re-instantiate an object from a flattened dictionary.

Versioning
----------

When an object is converted to YAML
the package version is stored.
But what happens if we later load the object
with a different package version?

Let's create another instance of ``MyObject``.

.. code-block:: pycon

    >>> o = MyObject("I am a 1.0.0!", num_repeat=2)
    >>> print(o)
    I am a 1.0.0! I am a 1.0.0!

And convert it to YAML.

.. code-block:: pycon

    >>> o_yaml = o.to_yaml_s()
    >>> print(o_yaml)
    $mypkg.MyObject==1.0.0:
      string: I am a 1.0.0!
      num_repeat: 2
    <BLANKLINE>

Loading it with a newer version of the package
works without problems.

.. code-block:: pycon

    >>> __version__ = "1.1.0"
    >>> o2 = audobject.from_yaml_s(o_yaml)
    >>> print(o2)
    I am a 1.0.0! I am a 1.0.0!

But if we load it with an older version,
a warning will be shown.
We can force it to show no warning at all,
or always show a warning
when the package version does not match
by adjusting
:attr:`audobject.config.PACKAGE_MISMATCH_WARN_LEVEL`.

.. skip: next

.. code-block:: python

    __version__ = "0.9.0"

    o3 = audobject.from_yaml_s(o_yaml)
    print(o3)

.. Silently apply the old-version state for the rest of the section.

.. invisible-code-block: python

    __version__ = "0.9.0"
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        o3 = audobject.from_yaml_s(o_yaml)

Now we pretend that we update the package to ``2.0.0``.
It includes a new version of ``MyObject``,
with a slightly changed ``__str__`` function.

.. code-block:: python

    __version__ = "2.0.0"

    class MyObject(audobject.Object):

        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return ",".join([self.string] * self.num_repeat)

Since the signature of the constructor has not changed,
the object will be created without problems.
However, when we print the object
the strings are now separated by comma.

.. code-block:: pycon

    >>> o3 = audobject.from_yaml_s(o_yaml)
    >>> print(o3)
    I am a 1.0.0!,I am a 1.0.0!

In the next release, we decide to introduce an argument
that let the user set a custom delimiter.

.. code-block:: python

    __version__ = "2.1.0"

    class MyObject(audobject.Object):

        def __init__(
                self,
                string: str,
                delimiter: str,
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.delimiter = delimiter
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return " ".join([self.string] * self.num_repeat)

If we now instantiate the object,
we will get an error,
because we are missing a value
for the new argument.

.. code-block:: pycon

    >>> audobject.from_yaml_s(o_yaml)
    Traceback (most recent call last):
        ...
    RuntimeError: Missing mandatory arguments ['delimiter'] while instantiating <class 'mypkg.MyObject'> from version '1.0.0' when using version '2.1.0'.

Since we want to be backward compatible,
we decide to release a bug fix,
where we initialize the new argument with a default value.

.. code-block:: python

    __version__ = "2.1.1"

    class MyObject(audobject.Object):

        def __init__(
                self,
                string: str,
                delimiter: str = ",",
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.delimiter = delimiter
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return " ".join([self.string] * self.num_repeat)

And in fact, it successfully creates the object again.
It works, because it now has a default value for the missing argument.

.. code-block:: pycon

    >>> o4 = audobject.from_yaml_s(o_yaml)
    >>> print(o4)
    I am a 1.0.0! I am a 1.0.0!

Finally, we will do it the other way round.
Create an object with version ``2.1.1``.

.. code-block:: pycon

    >>> o5 = MyObject("I am a 2.1.1!", num_repeat=2)
    >>> print(o5)
    I am a 2.1.1! I am a 2.1.1!

Convert it to YAML.

.. code-block:: pycon

    >>> o5_yaml = o5.to_yaml_s()
    >>> print(o5_yaml)
    $mypkg.MyObject==2.1.1:
      string: I am a 2.1.1!
      delimiter: ','
      num_repeat: 2
    <BLANKLINE>

And load it with ``1.0.0``.

.. skip: next

.. code-block:: python

    __version__ = "1.0.0"

    class MyObject(audobject.Object):

        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return " ".join([self.string] * self.num_repeat)

    o6 = audobject.from_yaml_s(o5_yaml)
    print(o6)

.. invisible-code-block: python

    __version__ = "1.0.0"

    class MyObject(audobject.Object):
        def __init__(self, string, *, num_repeat=1):
            self.string = string
            self.num_repeat = num_repeat
        def __str__(self):
            return " ".join([self.string] * self.num_repeat)

    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        o6 = audobject.from_yaml_s(o5_yaml)

In fact, it works, too.
However, a warning is given that an argument was ignored.

Dictionary
----------

:class:`audobject.Dictionary` implements a
:class:`audobject.Object` that can used like a dictionary.

.. code-block:: pycon

    >>> d = audobject.Dictionary(
    ...     string="I am a dictionary!",
    ...     pi=3.14159265359,
    ... )
    >>> print(d)
    $audobject.core.dictionary.Dictionary:
      string: I am a dictionary!
      pi: 3.14159265359
    <BLANKLINE>

We can use ``[]`` notation to access the
values of the dictionary.

.. code-block:: pycon

    >>> d["string"] = "Still a dictionary!"
    >>> d["new"] = None
    >>> print(d)
    $audobject.core.dictionary.Dictionary:
      string: Still a dictionary!
      pi: 3.14159265359
      new: null
    <BLANKLINE>

And update from another dictionary.

.. code-block:: pycon

    >>> d2 = audobject.Dictionary(
    ...     string="I will be a dictionary forever!",
    ...     object=MyObject("Hey, I am an object."),
    ... )
    >>> d.update(d2)
    >>> print(d)
    $audobject.core.dictionary.Dictionary:
      string: I will be a dictionary forever!
      pi: 3.14159265359
      new: null
      object:
        $mypkg.MyObject:
          string: Hey, I am an object.
          num_repeat: 1
    <BLANKLINE>

And we can read/write the dictionary from/to a file.

.. code-block:: pycon

    >>> file = "dict.yaml"
    >>> d.to_yaml(file)
    >>> d3 = audobject.from_yaml(file)
    >>> print(d3)
    $audobject.core.dictionary.Dictionary:
      string: I will be a dictionary forever!
      pi: 3.14159265359
      new: null
      object:
        $mypkg.MyObject:
          string: Hey, I am an object.
          num_repeat: 1
    <BLANKLINE>

Parameters
----------

You have probably used argparse_ before.
It is a package to write user-friendly command-line interfaces
that allows the user to define what arguments are required,
what are the expected types, default values, etc.

The idea behind :class:`audobject.Parameters` is similar
(in fact, we will see that i even has an interface to argparse_).
:class:`audobject.Parameters` is basically a collection of
named values that control the behaviour of an object.
Each value is wrapped in a :class:`audobject.Parameter`
object and has a specific type and default value,
possibly one of a set of choices.
And it can be bound a parameter to a specific versions.

Let's pick up the previous example and define two parameters.
A parameter that holds a string.

.. code-block:: pycon

    >>> string = audobject.Parameter(
    ...     value_type=str,
    ...     description="the string we want to repeat",
    ...     value="bar",
    ...     choices=["bar", "Bar", "BAR"],
    ... )
    >>> print(string)
    $audobject.core.parameter.Parameter:
      value_type: str
      description: the string we want to repeat
      value: bar
      default_value: null
      choices:
      - bar
      - Bar
      - BAR
      version: null
    <BLANKLINE>

And a parameter that defines how many times we want to repeat the string.

.. code-block:: pycon

    >>> repeat = audobject.Parameter(
    ...     value_type=int,
    ...     description="the number of times we want to repeat",
    ...     default_value=1,
    ... )
    >>> print(repeat)
    $audobject.core.parameter.Parameter:
      value_type: int
      description: the number of times we want to repeat
      value: 1
      default_value: 1
      choices: null
      version: null
    <BLANKLINE>

Now we combine the two parameters into a list.

.. code-block:: pycon

    >>> params = audobject.Parameters(
    ...     string=string,
    ...     num_repeat=repeat,
    ... )
    >>> print(params)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      bar    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  1      1        None                   the number of times we want to repeat  None

If we call the list,
we get a dictionary of parameter names and values.

.. code-block:: pycon

    >>> params()
    {'string': 'bar', 'num_repeat': 1}

We can access the values of the parameters using ``.`` notation.

.. code-block:: pycon

    >>> params.string = "BAR"
    >>> params.num_repeat = 2
    >>> print(params)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      BAR    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  2      1        None                   the number of times we want to repeat  None

If we try to assign a value that is not in choices,
we will get an error.

.. code-block:: pycon

    >>> params.string = "par"
    Traceback (most recent call last):
        ...
    ValueError: Invalid value 'par', expected one of ['bar', 'Bar', 'BAR'].

It is possible to assign a version (or a range of versions)
to a parameter.

.. code-block:: pycon

    >>> delim = audobject.Parameter(
    ...     value_type=str,
    ...     description="defines the delimiter",
    ...     default_value=",",
    ...     version=">=2.0.0,<3.0.0"
    ... )
    >>> params["delimiter"] = delim
    >>> print(params)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      BAR    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  2      1        None                   the number of times we want to repeat  None
    delimiter   ,      ,        None                   defines the delimiter                  >=2.0.0,<3.0.0

We can check if a parameter is available for a specific version.

.. code-block:: pycon

    >>> "1.0.0" in delim, "2.4.0" in delim
    (False, True)

We can also filter a list of parameters by version.

.. code-block:: pycon

    >>> params_v3 = params.filter_by_version("3.0.0")
    >>> print(params_v3)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      BAR    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  2      1        None                   the number of times we want to repeat  None

Or add them to a command line interface.

.. code-block:: pycon

    >>> import argparse
    >>> parser = argparse.ArgumentParser(prog="")
    >>> params.to_command_line(parser)
    >>> print(parser.format_help())
    usage:  [-h] [--string {bar,Bar,BAR}] [--num_repeat NUM_REPEAT]
            [--delimiter DELIMITER]
    <BLANKLINE>
    options:
      -h, --help            show this help message and exit
      --string {bar,Bar,BAR}
                            the string we want to repeat
      --num_repeat NUM_REPEAT
                            the number of times we want to repeat
      --delimiter DELIMITER
                            defines the delimiter (version: >=2.0.0,<3.0.0)
    <BLANKLINE>

Or update the values from a command line interface.

.. code-block:: pycon

    >>> args = parser.parse_args(
    ...     args=["--string=Bar", "--delimiter=;"]
    ... )
    >>> _ = params.from_command_line(args)
    >>> print(params)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      Bar    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  1      1        None                   the number of times we want to repeat  None
    delimiter   ;      ,        None                   defines the delimiter                  >=2.0.0,<3.0.0

It is possible to convert it into a file path
that keeps track of the parameters.

.. code-block:: pycon

    >>> params.to_path(sort=True)
    'delimiter[;]/num_repeat[1]/string[Bar]'

Last but not least, we can read/write the parameters from/to a file.

.. code-block:: pycon

    >>> file = "params.yaml"
    >>> params.to_yaml(file)
    >>> params2 = audobject.from_yaml(file)
    >>> print(params2)
    Name        Value  Default  Choices                Description                            Version
    ----        -----  -------  -------                -----------                            -------
    string      Bar    None     ['bar', 'Bar', 'BAR']  the string we want to repeat           None
    num_repeat  1      1        None                   the number of times we want to repeat  None
    delimiter   ;      ,        None                   defines the delimiter                  >=2.0.0,<3.0.0

.. _timedelta: https://docs.python.org/3/library/datetime.html#timedelta-objects
.. _argparse: https://docs.python.org/3/library/argparse.html
