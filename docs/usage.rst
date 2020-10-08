Usage
=====

The aim of :mod:`audobject` is to provide
a base class, namely :class:`audobject.Object`,
which allows it to convert the state
of an object to a YAML string and at
later stage recover the object from it.


.. jupyter-execute::
    :hide-code:

    import audobject


Object class
------------

Let's create a class that derives from :class:`audobject.Object`.

.. jupyter-execute::

    __version__ = '1.0.0'  # pretend we have a package version

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
            return ' '.join([self.string] * self.num_repeat)

Now we instantiate an object and print it.

.. jupyter-execute::

    o = MyObject('hello object!', num_repeat=2)
    print(o)

As expected we see that ``string`` is repeated ``num_repeat`` times.
But since we derived from :class:`audobject.Object`
we can also print a YAML representation of the object.

.. jupyter-execute::

    o_yaml = o.to_yaml_s()
    print(o_yaml)

As we see it holds the name of the class
and the values of the parameters
that were used to initialize the object.
This allows it to create a new instance
of the object from its YAML representation.

.. jupyter-execute::

    o2 = audobject.Object.from_yaml_s(o_yaml)
    print(o2)

We can also save the object to disk and
re-instantiate it from there.

.. jupyter-execute::

    file = 'my.yaml'
    o.to_yaml(file)
    o3 = audobject.Object.from_yaml(file)
    print(o3)

Hidden variable
---------------

In the constructor of ``MyObject`` we have assigned
every parameter to class variables with the same name.
This is the core concept we have to follow
when we derive from :class:`audobject.Object`.
Any other class variables we make private,
i.e. start with a ``_``.

For example, we could store the message
we want to print in a variable.

.. jupyter-execute::

    class MyObjectWithHiddenVariable(audobject.Object):
        def __init__(
                self,
                string: str,
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.num_repeat = num_repeat
            self._message = ' '.join([self.string] * self.num_repeat)

        @property
        def message(self) -> str:
            return self._message

        def __str__(self) -> str:
            return self._message

The new class still works as expected.

.. jupyter-execute::

    o = MyObjectWithHiddenVariable('hello object!', num_repeat=3)
    print(o)

And if we print,
we see that the new (hidden) variable is not stored.

.. jupyter-execute::

    o_yaml = o.to_yaml_s()
    print(o_yaml)

Yet, since we added a property for it,
we can still access it as if it was a variable of the instance.

.. jupyter-execute::

    print(o.message)

Object as variable
------------------

It is possible to have instances of :class:`audobject.Object`
as variables.
For instance, we can define the following class.

.. jupyter-execute::

    class MySuperObject(audobject.Object):
        def __init__(
                self,
                obj: MyObject,
        ):
            self.obj = obj

        def __str__(self) -> str:
            return f'[{str(self.obj)}]'

And initialize it with an instance of ``MyObject``.

.. jupyter-execute::

    o = MyObject('eat me!')
    w = MySuperObject(o)
    print(w)

This translates to the following YAML string.

.. jupyter-execute::

    w_yaml = w.to_yaml_s()
    print(w_yaml)

From which we can re-instantiate the object.

.. jupyter-execute::

    w2 = audobject.Object.from_yaml_s(w_yaml)
    print(w2)

Value resolver
--------------

As long as the type of our variables is one of
``(None, Object, str, int, float, bool, list, dict, datetime.datetime)``,
it is ensured that we get a clean YAML file.
Other types may be encoded using the ``!!python/object`` tag
and clutter the YAML syntax.

To illustrate this, let's use an instance of timedelta_.

.. jupyter-execute::

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

.. jupyter-execute::

    delta = timedelta(
        days=50,
        seconds=27,
        microseconds=10,
        milliseconds=29000,
        minutes=5,
        hours=8,
        weeks=2
    )
    d = MyDeltaObject(delta)
    print(d)

But if we convert it to YAML,
we'll see a warning.

.. jupyter-execute::
    :stderr:

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

.. jupyter-execute::

    class DeltaResolver(audobject.ValueResolver):

        def decode(self, value: dict) -> timedelta:
            return timedelta(
                days=value['days'],
                seconds=value['seconds'],
                microseconds=value['microseconds'],
            )

        def encode(self, value: timedelta) -> dict:
            return {
                'days': value.days,
                'seconds': value.seconds,
                'microseconds': value.microseconds,
            }

        def encode_type(self):
            return dict

To apply our custom resolver to the
``delta`` variable, we use
:meth:`audobject.init_object_decorator`
on the ``__init__`` function of our class.

.. jupyter-execute::

    class MyResolvedDeltaObject(audobject.Object):

        @audobject.init_object_decorator({'delta': DeltaResolver})
        def __init__(
                self,
                delta: timedelta,
        ):
            self.delta = delta

        def __str__(self) -> str:
            return str(self.delta)

Now, we don't get a warning
and the ``!!python/object`` tag has disappeared.

.. jupyter-execute::

    d = MyResolvedDeltaObject(delta)
    d_yaml = d.to_yaml_s()
    print(d_yaml)

Object ID
---------

Every object has an ID.

.. jupyter-execute::

    o = MyObject('I am unique!', num_repeat=2)
    print(o.id)

Objects with exact same properties share the same ID.

.. jupyter-execute::

    o2 = MyObject('I am unique!', num_repeat=2)
    print(o.id == o2.id)

When an object is serialized the ID does not change.

.. jupyter-execute::

    o3 = audobject.Object.from_yaml_s(o.to_yaml_s())
    print(o3.id == o.id)

Objects with different properties get different IDs.

.. jupyter-execute::

    o4 = MyObject('I am different!', num_repeat=2)
    print(o.id == o4.id)

Versioning
----------

When an object is converted to YAML
the package version is stored.
But what happens if we later load the object
with a different package version?

Let's create another instance of ``MyObject``.

.. jupyter-execute::

    o = MyObject('I am a 1.0.0!', num_repeat=2)
    print(o)

And convert it to YAML.

.. jupyter-execute::

    o_yaml = o.to_yaml_s()
    print(o_yaml)

Now we pretend that we update the package to ``2.0.0``.
It includes a new version of ``MyObject``,
with a slightly changed ``__str__`` function.

.. jupyter-execute::

    __version__ = '2.0.0'

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
            return ','.join([self.string] * self.num_repeat)

Since the signature of the constructor has not changed,
the object will be created without problems.
However, when we print the object
the strings are now separated by comma.

.. jupyter-execute::

    o2 = audobject.Object.from_yaml_s(o_yaml)
    print(o2)

In the next release, we decide to introduce an argument
that let the user set a custom delimiter.

.. jupyter-execute::

    __version__ = '2.1.0'

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
            return ' '.join([self.string] * self.num_repeat)

If we now instantiate the object,
we will get an error,
because we are missing a value
for the new argument.

.. jupyter-execute::
    :stderr:
    :raises:

    audobject.Object.from_yaml_s(o_yaml)

Since we want to be backward compatible,
we decide to release a bug fix,
where we initialize the new argument with a default value.

.. jupyter-execute::

    __version__ = '2.1.1'

    class MyObject(audobject.Object):
        def __init__(
                self,
                string: str,
                delimiter: str = ',',
                *,
                num_repeat: int = 1,
        ):
            self.string = string
            self.delimiter = delimiter
            self.num_repeat = num_repeat

        def __str__(self) -> str:
            return ' '.join([self.string] * self.num_repeat)

And in fact, it successfully creates the object again.
It works, because it now has a default value for the missing argument.

.. jupyter-execute::

    o3 = audobject.Object.from_yaml_s(o_yaml)
    print(o3)

Finally, we will do it the other way round.
Create an object with version ``2.1.1``.

.. jupyter-execute::

    o4 = MyObject('I am a 2.1.1!', num_repeat=2)
    print(o4)

Convert it to YAML.

.. jupyter-execute::

    o4_yaml = o4.to_yaml_s()
    print(o4_yaml)

And load it with ``1.0.0``.

.. jupyter-execute::
    :stderr:

    __version__ = '1.0.0'

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
            return ' '.join([self.string] * self.num_repeat)

    o5 = audobject.Object.from_yaml_s(o4_yaml)
    print(o5)

In fact, it works, too.
However, a warning is given that an argument was ignored.

Dictionary
----------

:class:`audobject.Dictionary` implements a
:class:`audobject.Object` that can used like a dictionary.

.. jupyter-execute::

    d = audobject.Dictionary(
        string='I am a dictionary!',
        pi=3.14159265359,
    )
    print(d)

We can use ``[]`` notation to access the
values of the dictionary.

.. jupyter-execute::

    d['string'] = 'Still a dictionary!'
    d['new'] = None
    print(d)

And update from another dictionary.

.. jupyter-execute::

    d2 = audobject.Dictionary(
        string='I will be a dictionary forever!',
        object=MyObject('Hey, I am an object.'),
    )
    d.update(d2)
    print(d)

And we can read/write the dictionary from/to a file.

.. jupyter-execute::

    file = 'dict.yaml'
    d.to_yaml(file)
    d3 = audobject.Object.from_yaml(file)
    print(d3)

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

.. jupyter-execute::

    string = audobject.Parameter(
        value_type=str,
        description='the string we want to repeat',
        value='bar',
        choices=['bar', 'Bar', 'BAR'],
    )
    print(string)

And a parameter that defines how many times we want to repeat the string.

.. jupyter-execute::

    repeat = audobject.Parameter(
        value_type=int,
        description='the number of times we want to repeat',
        default_value=1,
    )
    print(repeat)

Now we combine the two parameters into a list.

.. jupyter-execute::

    params = audobject.Parameters(
        string=string,
        num_repeat=repeat,
    )
    print(params)

If we call the list,
we get a dictionary of parameter names and values.

.. jupyter-execute::

    params()

We can access the values of the parameters using ``.`` notation.

.. jupyter-execute::

    params.string = 'BAR'
    params.num_repeat = 2
    print(params)

If we try to assign a value that is not in choices,
we will get an error.

.. jupyter-execute::
    :stderr:
    :raises:

    params.string = 'par'

It is possible to assign a version (or a range of versions)
to a parameter.

.. jupyter-execute::

    delim = audobject.Parameter(
        value_type=str,
        description='defines the delimiter',
        default_value=',',
        version='>=2.0.0,<3.0.0'
    )
    params['delimiter'] = delim
    print(params)

We can check if a parameter is available for a specific version.

.. jupyter-execute::

    '1.0.0' in delim, '2.4.0' in delim

We can also filter a list of parameters by version.

.. jupyter-execute::

    params_v3 = params.filter_by_version('3.0.0')
    print(params_v3)

Or add them to a command line interface.

.. jupyter-execute::

    import argparse

    parser = argparse.ArgumentParser()
    params.to_command_line(parser)
    print(parser.format_help())

Or update the values from a command line interface.

.. jupyter-execute::

    args = parser.parse_args(
        args=['--string=Bar', '--delimiter=;']
    )
    params.from_command_line(args)
    print(params)

It is possible to convert it into a file path
that keeps track of the parameters.

.. jupyter-execute::

    params.to_path(sort=True)

Last but not least, we can read/write the parameters from/to a file.

.. jupyter-execute::

    file = 'params.yaml'
    params.to_yaml(file)
    params2 = audobject.Object.from_yaml(file)
    print(params2)

.. _timedelta: https://docs.python.org/3/library/datetime.html#timedelta-objects
.. _argparse: https://docs.python.org/3/library/argparse.html
