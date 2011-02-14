from reviewboard.webapi.resources import WebAPIResource

from djblets.webapi.resources import register_resource_for_model
from reviewboard.webapi.resources import review_request_resource
from reviewboard.reviews.models import ReviewRequest


class ReviewRequestResource(WebAPIResource):
    model = ReviewRequest
    name = 'my-request'
    plural_name = 'my-requests'
    allowed_methods = ('GET')
    uri_object_key = 'id'
    fields = ('id')
      
    def get(self, request, *args, **kwargs):
        review_session = self.get_object(request, *args, **kwargs)
        
        return 200, {
            self.item_result_key: {
                'review_last_updated': review_session.last_updated,
                'review_summary': review_session.summary,
                'review_request_id': review_session.id,
            }
        }
        
        
    
    def get_object(self, request, local_site_name=None, *args, **kwargs):
        review_request_id = kwargs.get('id')
        return review_request_resource.get_object(request, review_request_id, local_site_name, *args, **kwargs)

    
reviewing_session_resource = ReviewRequestResource()
