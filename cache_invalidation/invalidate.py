import sys, datetime, settings
from level3client import Level3Service
from boto.cloudfront import CloudFrontConnection

urls = sys.argv
urls.remove('invcache.py')
scope = settings.level3scope
key_id = settings.level3key
secret = settings.level3secret
service = Level3Service(key_id, secret, method='POST')
result = service('invalidations/%s' % scope, post_data="""
<paths>
%s
</paths>
""" % ('\n'.join(['<path>%s</path>' % url for url in urls]))
)

conn = CloudFrontConnection( settings.awscfkey, settings.awscfsecret )
invreq = conn.create_invalidation_request( settings.awscfdistribution, urls)

print "Level3 Invalidation Request:"
print result.dom.toprettyxml()

print "CloudFront Invalidation Status:"
print invreq.status
