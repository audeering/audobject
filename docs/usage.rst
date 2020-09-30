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
``(None, Object, str, int, float, bool, list, dict)``,
it is ensured that we can correctly
re-instantiate an instance from YAML.
Variables with other types
will be converted as to a string by calling ``repr()``,
which is usually not what we want.

To illustrate this, let's use an instance of ``datetime``.

.. jupyter-execute::

    from datetime import datetime

    class MyDateObject(audobject.Object):

        def __init__(
                self,
                date: datetime,
        ):
            self.date = date

        def __str__(self) -> str:
            return self.date.strftime('%Y-%m-%d %H:%M:%S.%f')


As before, we can create an instance and print it.

.. jupyter-execute::

    d = MyDateObject(datetime.now())
    print(d)

But if we convert it to YAML,
we'll see a warning.

.. jupyter-execute::
    :stderr:

    d_yaml = d.to_yaml_s()
    print(d_yaml)

And in fact, our code will break
if we re-instantiate the object
and try to print it.

.. jupyter-execute::
    :stderr:
    :raises:

    d2 = audobject.Object.from_yaml_s(d_yaml)
    print(d2)

The problem comes from the fact
that the type of the ``date`` variable
turned from ``datetime`` to ``str``.
To avoid this we can provide a resolver,
which properly encodes and decodes
the variable while retaining its type.

.. jupyter-execute::

    class DatetimeResolver(audobject.ValueResolver):

        def encode(self, value: datetime) -> str:
            return value.strftime('%Y-%m-%d %H:%M:%S.%f')

        def decode(self, value: str) -> datetime:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')


    class MySafeDateObject(audobject.Object):

        def __init__(
                self,
                date: datetime,
        ):
            self.date = date
            self._value_resolver['date'] = DatetimeResolver()

        def __str__(self) -> str:
            return self.date.strftime('%Y-%m-%d %H:%M:%S.%f')

Now, the following code works as expected.

.. jupyter-execute::

    d = MySafeDateObject(datetime.now())
    d_yaml = d.to_yaml_s()
    d2 = audobject.Object.from_yaml_s(d_yaml)
    print(d2)

If we don't want to define a resolver class,
we can achieve the same with ``lambda`` expressions.

.. jupyter-execute::

    class MySafeDateObject2(audobject.Object):

        def __init__(
                self,
                date: datetime,
        ):
            self.date = date
            self._value_resolver['dt'] = (
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S.%f'),
                lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f'),
            )

        def __str__(self) -> str:
            return self.date.strftime('%Y-%m-%d %H:%M:%S.%f')


    d = MySafeDateObject2(datetime.now())
    d_yaml = d.to_yaml_s()
    d2 = audobject.Object.from_yaml_s(d_yaml)
    print(d2)
