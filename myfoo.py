from abc import ABCMeta, abstractmethod, abstractproperty

class AbstractMyFoo:
    __metaclass__ = ABCMeta

    @abstractmethod
    def support_this(self):
        pass

class ConcreteMyFoo(AbstractMyFoo):

    def support_this(self):
        print "HEY"

# AbstractMyFoo.register(ConcreteMyFoo)
assert issubclass(ConcreteMyFoo, AbstractMyFoo)
assert isinstance(ConcreteMyFoo(), AbstractMyFoo)

c = ConcreteMyFoo()
c.support_this()
