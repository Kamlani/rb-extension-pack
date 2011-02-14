from reviewboard.webapi.resources import WebAPIResource

from djblets.webapi.resources import register_resource_for_model

from reviewboard.reviews.models import ReviewRequest


class ReviewRequestResource(WebAPIResource):
    model = ReviewRequest
    name = 'my-request'
    plural_name = 'my-requests'
    allowed_methods = ('GET')
    uri_object_key = 'id'
    fields = ('id')
  
	import pdb;pdb.set_trace()
	
    def get(self, request, *args, **kwargs):
        return 200, {}
    
    def get_object(self, request, *args, **kwargs):
        review_request_id = kwargs.get('id')
        review_request = ReviewRequest.objects.get(id=review_request_id)
        return review_request  

    
reviewing_session_resource = ReviewRequestResource()
