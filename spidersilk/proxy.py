import urlparse
from urllib import quote as urlquote

from twisted.web.proxy import ReverseProxyResource
from twisted.web.server import NOT_DONE_YET


class ForwardedReverseProxyResource(ReverseProxyResource):

      def getChild(self, path, request):
            return ForwardedReverseProxyResource(
                  self.host, self.port, self.path + '/' + urlquote(path, safe=''),
                  self.reactor)


      def render(self, request):
            if self.port == 80:
                  host = self.host
            else:
                  host = "%s:%d" % (self.host, self.port)
            request.received_headers['x-forwarded-host'] = request.received_headers['host']
            request.received_headers['host'] = host

            request.content.seek(0, 0)
            headers = request.getAllHeaders()
            qs = urlparse.urlparse(request.uri)[4]
            if qs:
                  rest = self.path + '?' + qs
            else:
                  rest = self.path
            clientFactory = self.proxyClientFactoryClass(
                  request.method, rest, request.clientproto,
                  headers, request.content.read(), request)
            self.reactor.connectTCP(self.host, self.port, clientFactory)
            return NOT_DONE_YET


