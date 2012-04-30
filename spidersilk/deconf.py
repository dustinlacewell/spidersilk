class RequiredParameterError(Exception): pass
class CyclicalDependencyError(Exception): pass

class Deconfigurable(object):
    '''
    A class that has rich(ish) keyword-parameter handling including explicit
    handling of required parameters and declaration of parameter dependencies.

    Keyword parameter processing will be performed for any method on the
    Configurable that is decorated with the 'parameter' decorator. Each of these
    decorated methods performs the processing specific to that parameter.

    >>> @parameter('foo')
    >>> def handle_foo(self, kwargs):
    ...    self.foo = kwargs.get('foo')
    ...    return self.foo

    REQUIRED PARAMETERS:

    Parameters are required by default. This means that a RequiredParameterError
    will be raised if the Configurable.__init__ doesn't recieve the designated
    named argument. 

    Passing `required=False` to @parameter will prevent the parameter from
    raising RequiredParameterError if the parameter isn't provided a value. If
    the parameter does not return a default value then None will be used.

    >>> @parameter('foo', required=False)
    >>> def handle_foo(self, kwargs):
    ...    self.foo = kwargs.get('foo', 'bar')
    ...    return self.foo


    DEPENDENCY PARAMETERS:
   
    Sometimes we will want to defer processing of a parameter until some other
    parameter has been processed first. To do so, simply pass a list of
    dependencies, `depends_on`, to @parameter.

    >>> @parameter('bar', depends_on=('foo', ))
    >>> def handle_bar(self, kwargs):
    ...     self.bar = kwargs.get('bar')
    ...     return self.bar
    '''

    def __init__(self, **kwargs):
        self._param_methods = self._get_param_methods()
        self._param_vals = {}
        for param, method in self._param_methods.items():
            self._process_param(param, method, kwargs)
        
    def _get_param_methods(self):
        methods = {}
        for name in dir(self):
            attr = getattr(self, name)
            if callable(attr) and hasattr(attr, '__param__'):
                methods[attr.__param__] = attr
        return methods

    def _process_param(self, param, method, kwargs, chain=None):
        if chain == None:
            chain = []
        chain.append(param)
        # process dependencies
        deps = getattr(method, '__dependencies__', [])
        for depname in deps:
            # cyclical dependency
            if depname in chain:
                msg = "Cyclical dependency discovered while processing '%s'."
                ctx = (chain[0], )
                raise CyclicalDependencyError(msg % ctx)
            dep_method = self._param_methods.get(depname, None)
            # erroneous dependency
            if dep_method is None:
                msg = "'%s' depends on '%s' parameter but %s has no method '%s'."
                ctx = (param, depname, 
                       self.__class__, '_arg_%s' % depname)
                raise RequiredParameterError(msg % ctx)
            # new dependency
            if depname not in self._param_vals:
                self._process_param(depname, dep_method, kwargs, chain=chain)
            # failed dependency
            if depname not in self._param_vals:
                msg = "'%s' object missing required '%s' parameter."
                ctx = (self.__class__.__name__, depname)
                raise RequiredParameterError(msg % ctx)                

        self._param_vals[param] = method(kwargs)

def parameter(param, required=True, depends_on=tuple()):
    def decorator(f):
        def wrapper(self, kwargs):
            if required == True:
                if param not in kwargs:
                    msg = "'%s' object missing required '%s' parameter."
                    ctx = (self.__class__.__name__, param)
                    raise RequiredParameterError(msg % ctx)
            return f(self, kwargs)
        setattr(wrapper, '__param__', param)
        setattr(wrapper, '__required__', required)
        setattr(wrapper, '__dependencies__', depends_on)
        return wrapper
    return decorator
