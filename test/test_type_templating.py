from type_templating import Template, TemplateParameter, TemplateExpression


def test_basic():
    K = TemplateParameter('K')
    V = TemplateParameter('V')

    class Foo(metaclass=Template[K, V]):
        @classmethod
        def get_k(cls):
            return cls.__args[K]

        @classmethod
        def get_v(cls):
            return cls.__args[V]

    assert isinstance(Foo, Template)
    assert isinstance(Foo[K, 2], TemplateExpression)
    assert issubclass(Foo[1, 2], Foo)
    assert isinstance(Foo[1, 2](), Foo)
    assert Foo[1, 2].get_k() == 1
    assert Foo[1, 2].get_v() == 2

    class Bar(Foo[1, 2], metaclass=Template[K]):
        pass

    assert Bar[3].get_k() == 1
    assert Bar[3].get_v() == 2

    class Baz(Foo[K, K], metaclass=Template[K]):
        pass

    assert Baz[3].get_k() == 3
    assert Baz[3].get_v() == 3

    print("Baz.mro", Baz[3].mro())

    class Outer(Baz[K], Foo[1, 2], metaclass=Template[K]):
        def __init__(self, s):
            self.s = s

        def __newinferred__(cls, s):
            return Outer[len(s)](s)

    assert Outer[4].get_k() == 4
    assert Outer[4].get_v() == 4
    assert Outer[4] is Outer[4]

    print("Outer.mro", Outer[4].mro())

    print(Outer("Hello world"))


def test_doc_example():
    T = TemplateParameter('T')
    N = TemplateParameter('N')

    # Sequence is a template taking one argument
    class Sequence(metaclass=Template[T]):
        pass

    # MyList is a template taking two arguments, where the first is passed
    # down for use in the `Sequence` base class.
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

    m = MyList[int, 3]()
    assert isinstance(m, MyList[int, 3])
    assert isinstance(m, MyList)
    assert isinstance(m, Sequence[int])
    assert isinstance(m, Sequence)

    m = MyList(["Hello", "World"])
    assert isinstance(m, MyList[str, 2])


def test_base_class_as_parameter():
    T = TemplateParameter('T')
    class HasBaseOf(T, metaclass=Template[T]):
        pass
    class Test:
        pass
    v = HasBaseOf[Test]()
    assert isinstance(v, Test)
    v = HasBaseOf[int]()
    assert isinstance(v, int)

