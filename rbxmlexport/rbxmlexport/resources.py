from reviewboard.webapi.resources import WebAPIResource

from djblets.webapi.resources import register_resource_for_model
from djblets.webapi.core import NameArray
from reviewboard.webapi.resources import review_request_resource
from reviewboard.reviews.models import ReviewRequest
from reviewboard.reviews.models import Review



class ReviewRequestResource(WebAPIResource):
    model = ReviewRequest
    name = 'ExportXMLRequest'
    plural_name = 'ExportXMLRequests'
    allowed_methods = ('GET')
    uri_object_key = 'id'
    fields = ('id')
    

      
    def get(self, request, *args, **kwargs):
        my_review_request = self.get_object(request, *args, **kwargs)

        ReviewXML = []
      
        for review in my_review_request.get_public_reviews():        
            ReviewXML.append(self.BuildReview(review))

        return 200, {
            self.item_result_key: {
                                    'Reviews' : NameArray(None,"Review",ReviewXML)
            }
        }
    
    def get_object(self, request, local_site_name=None, *args, **kwargs):
        review_request_id = kwargs.get('id')
        return review_request_resource.get_object(request, review_request_id, local_site_name, *args, **kwargs)

    def BuildReview(self, review):
        Review = []
 
        Review.append(NameArray(None,"UserName",[review.user.username]))

        ResponsesXML = self.build_response(review)
        if ResponsesXML is not None:
            Review.append(ResponsesXML)
       
        return NameArray(None,None,Review)


    def build_response(self, review):

        if review.body_top is not u'':
            ReviewResponseXML = []
            ReviewResponseXML.append(NameArray(None,"Text",[review.body_top]))

            ReviewComments = []
            counter = 0
            for reply in review.public_replies():
                ReviewComments.append(reply.body_top)
                counter = 1

            if counter is not 0:
                ReviewResponseXML.append(NameArray("Comments","Comment",ReviewComments))
            
            return NameArray("Response",None,ReviewResponseXML)

        return None



#    def build_codeSnippet(self, review):  TODO
#    def build screenshotSnippet(self, review): TODO

    

reviewing_session_resource = ReviewRequestResource()

































        #for comment in review.comments.all():
         #  ReviewComments.append(comment.text)










   # def BuildReview(self, review):
  #      ReviewParent = []
 #       ReviewParent.append(review.user.username)
#
  #      ReviewCommentsParent = []
 #       ReviewCommentsParent.append(review.body_top)
#
      #  ReviewCommentsChild = []
     #   for reply in review.public_replies():
    #        ReviewCommentsChild.append(reply.body_top)
   #     ReviewCommentsParent.append(ReviewCommentsChild)
  #      
 #       ReviewParent.append(ReviewCommentsParent)
#        return ReviewParent
    



