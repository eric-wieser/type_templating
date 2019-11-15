"""
C++-style type templating for python

.. autoclass:: Template

.. autoclass:: TemplateParameter

.. autoclass:: TemplateExpression

.. data:: __version__

    The version of this package
"""
__all__ = [
    'TemplateParameter',
    'Template',
    'TemplateExpression',
]

from ._version import __version__


class TemplateParameter:
    """
    A parameter used in a template specification.

    Name is used only for display purposes
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


def _make_template_name(name, args) -> str:
    return "{}[{}]".format(
        name, ', '.join(
            a.name if isinstance(a, TemplateParameter) else repr(a)
            for a in args
        )
    )


def _mangle(name, member):
    return '_{}__{}'.format(name.lstrip('_'), member)


class _TemplateSpec:
    """
    Return type of ``Template[K]``.

    This should be used as a metaclass, see :class:`Template` for more info.
    """
    def __init__(self, params):
        assert all(isinstance(p, TemplateParameter) for p in params)
        self.params = params

    def __repr__(self):
        return _make_template_name('Template', self.params)

    def __call__(self, name, bases, dict):
        return Template(name, bases, dict, params=self.params)


class _TemplateMeta(type):
    """ Meta-meta-class helper to enable ``Template[K]`` """
    def __getitem__(cls, items) -> _TemplateSpec:
        if not isinstance(items, tuple):
            items = (items,)
        return _TemplateSpec(items)


class Template(type, metaclass=_TemplateMeta):
    r"""
    The main mechanism for declaring template types.

    The result of ``type(SomeTemplate)``.

    Use as::

        T = TemplateParameter('T')
        N = TemplateParameter('N')

        # Sequence is a template taking one argument
        class Sequence(metaclass=Template[T]):
            pass


        # MyList is a template taking two arguments, where the first
        # is passed down for use in the `Sequence` base class.
        class MyList(Sequence[T], metaclass=Template[T, N]):
            def __init__(self, value=None):
                # self.__args contains the arguments values
                T_val = self.__args[T]
                N_val = self.__args[N]
                if value is None:
                    self.value = [T_val()] * N_val
                else:
                    assert len(value) == N_val
                    self.value = value

            def __newinferred__(cls, value):
                ''' This is used to infer type arguments '''
                T_val = type(value[0])
                N_val = len(value)
                return cls[T_val, N_val](value)

        assert isinstance(MyList, Template)

        m = MyList[int, 3]()
        assert isinstance(m, MyList[int, 3])
        assert isinstance(m, MyList)
        assert isinstance(m, Sequence[int])
        assert isinstance(m, Sequence)

        m = MyList(["Hello", "World"])
        assert isinstance(m, MyList[str, 2])

    .. attribute:: __base__

        The class definition use to define this template.
        Note that this is simply used as a base class, hence why it appears
        under this attribute. The base classes declared in the class definition
        will end up either in ``__expr_bases__`` or ``__base__.__bases__``.

    .. attribute:: __params__

        The list of template parameters taken by this template

    .. attribute:: __expr_bases__

        The list of :class:`TemplateExpression`\ s which should be expanded
        with the template parameters.
    """
    def __new__(metacls, name, bases, dict_, *, params):
        bases_no_templates = []
        base_template_exprs = []
        for b in bases:
            if isinstance(b, TemplateExpression):
                bases_no_templates += b.template.__bases__
                base_template_exprs.append(b)
            else:
                bases_no_templates.append(b)

        d = dict_.copy()
        q = d['__qualname__']
        d['__qualname__'] = q+".__base__"
        base = type(name+".__base__", tuple(bases_no_templates), d)
        return type.__new__(metacls, name, (base,), dict(
            __expr_bases__=tuple(base_template_exprs),
            __params__=params,
            __qualname__=q,

            # private dictionary of existing template instantiations
            _instantiations={},
        ))

    def __init__(cls, *args, **kwargs): pass

    def __subclasscheck__(cls, subclass):
        for c in subclass.mro():
            if getattr(c, '__template__', None) == cls:
                return True
        return False

    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __getitem__(cls, items):
        if not isinstance(items, tuple):
            items = (items,)
        if len(items) != len(cls.__params__):
            raise TypeError(
                "{} expected {} template arguments ({}), got {}".format(
                    cls,
                    len(cls.__params__), cls.__params__, len(items)
                )
            )
        if any(isinstance(i, TemplateParameter) for i in items):
            return TemplateExpression(cls, items)
        else:
            return TemplateExpression(cls, items)._substitute({})

    def __call__(cls, *args, **kwargs):
        """ Construct a template without template arguments, inferring them """
        try:
            f = cls.__base__.__newinferred__
        except AttributeError:
            pass
        else:
            i = f(cls, *args, **kwargs)
            if not isinstance(i, cls):
                raise TypeError(
                    "__newinferred__ should return a {}, but instead returned "
                    "a {}.".format(cls, type(i))
                )
            return i
        raise TypeError(
            "No type arguments passed to {}, and __newinferred__ is not "
            "defined".format(cls)
        )


class TemplateExpression:
    """
    The result of ``SomeTemplate[T]`` or ``SomeTemplate[T, 1]``

    Note that this is not used if the full set of arguments are specified.
    """
    def __init__(self, template, args):
        self.template = template
        self.args = args

    def __repr__(self):
        return _make_template_name(self.template.__qualname__, self.args)

    def _substitute(self, arg_values: dict):
        """
        Replace remaining TemplateParameters with values.

        Used during template instantiation, don't call directly.
        """
        args = tuple([
            arg_values[a] if isinstance(a, TemplateParameter) else a
            for a in self.args
        ])
        try:
            return self.template._instantiations[args]
        except KeyError:
            arg_dict = {
                p: a
                for p, a, in zip(self.template.__params__, args)
            }
            bases = tuple(
                expr._substitute(arg_dict)
                for expr in self.template.__expr_bases__
            ) + self.template.__bases__
            inst = type(
                _make_template_name(self.template.__qualname__, args),
                bases, {
                    _mangle(self.template.__name__, 'args'): arg_dict,
                    '__template__': self.template,
                }
            )
            self.template._instantiations[args] = inst
            return inst
