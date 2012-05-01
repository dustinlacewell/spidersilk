from twisted.application import internet, service
from twisted.web import static, server, vhost, script, proxy

from deconf import Deconfigurable, parameter

class Domain(Deconfigurable):
    @parameter('hostname', required=True)
    def _arg_hostname(self, kwargs):
        self.hostname = kwargs.get('hostname')
        return self.hostname

    @parameter('resource', required=True)
    def _arg_resource(self, kwargs):
        self.resource = kwargs.get('resource')
        return self.resource

class Httpd(Deconfigurable):
    def __init__(self, *args, **kwargs):
        super(Httpd, self).__init__(*args, **kwargs)
        root = vhost.NameVirtualHost()
        root.default = self.default.resource
        for domain in self.domains:
            root.addHost(domain.hostname, domain.resource)
        site = server.Site(root)
        self.application = service.Application('spidersilk')
        services = service.IServiceCollection(self.application)
        self.server = internet.TCPServer(int(self.port), site)
        self.server.setServiceParent(services)

    @parameter('port')
    def _arg_port(self, kwargs):
        self.port = kwargs.get('port', 80)

    @parameter('domains', required=True)
    def _arg_domains(self, kwargs):
        self.domains = kwargs.get('domains')
        if len(self.domains) < 1:
            msg = "Httpd 'domains' parameter must contain at least one instantiated Domain object"
            raise ValueError(msg)
        for domain in self.domains:
            if not isinstance(domain, Domain):
                msg = "Httpd 'domains' parameter must only contain Domain instances."
                raise ValueError(msg)
        return self.domains
        
    @parameter('default', required=True, depends_on=('domains', ))
    def _arg_default(self, kwargs):
        default_hostname = kwargs.get('default')
        self.default = None
        for domain in self.domains:
            if default_hostname == domain.hostname:
                self.default = domain
        if self.default is None:
            msg = "Httpd 'default' parameter must specify the hostname of a provided Domain object"
            raise ValueError(msg)
        return self.default
        
