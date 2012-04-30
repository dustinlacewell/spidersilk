spidersilk
==========

Spidersilk is an attempt at making an easy to use library for configuring a
twisted.web webserver. To install simply invoke the standard Python setup.py
script:


    $ python setup.py install


Once installed you can use objects imported from spidersilk to define how your
twisted.web resources should be hosted. The main objects involved are
`spidersilk.Httpd` and `spidersilk. The following is an extremely simple example
of hosting two twisted.web resources:


    from twisted.web.static import File
    from twisted.web.proxy import ReverseProxyResource

    from spidersilk import Domain, Httpd

    application = Httpd(
        port = 80,
        default = 'example.com',
        domains = [
            Domain(
                hostname='example.com',
                resource=File('/var/www/html'),
            ),
            Domain(
                hostname='wsgi.ldlework.com',
                resource=ReverseProxyResource('localhost', 8088, ''),
            ),
        ],
    ).application


In this example, after the imports, we begin by initializing a `spiderweb.Httpd`
instance. It has a few named arguments, like what port to host on. The `default`
parameter specifies the hostname of the Domain resource that should be served if
the requet does not match any other hostname. Then, we specify a list of
initialized `spidersilk.Domain` objects each of which declares what virtual-host
the corresponding resource should be hosted under.

The first `Domain` object uses a `twisted.web.static.File` resource for serving
static media from `/var/www/html` like Apache would do by default. The second
`Domain` object declares that for the `wsgi.example.com` subdomain that the
request should be reverse-proxied to seperate webserver running on the local 8088
port.

Finally, to start your new spidersilk server simply point `twistd` at your new formated tac file:


    $ twistd -noy spidersilk.tac