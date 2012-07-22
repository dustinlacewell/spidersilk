from spidersilk.deconf import Deconfigurable, parameter

class Domain(Deconfigurable):
    @parameter('hostname', required=True)
    def _arg_hostname(self, kwargs):
        self.hostname = kwargs.get('hostname')
        return self.hostname

    @parameter('resource', required=True)
    def _arg_resource(self, kwargs):
        self.resource = kwargs.get('resource')
        return self.resource

