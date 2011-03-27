from django.template.context import RequestContext
from djblets.webapi.core import NameArray

from reviewboard.reviews.models import ReviewRequest
from reviewboard.webapi.resources import review_request_resource
from reviewboard.webapi.resources import WebAPIResource
from reviewboard.reviews.views import get_file_chunks_in_range


class ReviewRequestResource(WebAPIResource):
    model = ReviewRequest
    name = 'ExportXMLRequest'
    plural_name = 'ExportXMLRequests'
    allowed_methods = ('GET')
    uri_object_key = 'id'
    fields = ('id')
  
    def get(self, request, *args, **kwargs):
        my_review_request = self.get_object(request, *args, **kwargs)

        review_request_xml = []
        if my_review_request.submitter.username: review_request_xml.append(NameArray("user",None,[my_review_request.submitter.username]))
        if my_review_request.summary: review_request_xml.append(NameArray("summary",None,[my_review_request.summary]))  
        if my_review_request.description: review_request_xml.append(NameArray("description",None,[my_review_request.description]))
        if my_review_request.testing_done: review_request_xml.append(NameArray("testing",None,[my_review_request.testing_done]))
        if my_review_request.changenum: review_request_xml.append(NameArray("changenum",None,[my_review_request.changenum]))
        if my_review_request.bugs_closed: review_request_xml.append(NameArray("bugs",None,[my_review_request.bugs_closed]))
        if my_review_request.branch: review_request_xml.append(NameArray("branch",None,[my_review_request.branch]))

        people_array = []
        for person in my_review_request.target_people.all():
            people_array.append(NameArray("user",None,[person.username]))
        if len(people_array): review_request_xml.append(NameArray("people",None,people_array))

        group_array = []
        for group in my_review_request.target_groups.all():
            people_array.append(NameArray("user",None,[group.display_name]))
        if len(group_array): review_request_xml.append(NameArray("group",None,group_array))

        review_xml = []
        for review in my_review_request.get_public_reviews():        
            current_review = self.build_review(request,review)
            if current_review: review_xml.append(current_review)

        return 200, {
            self.item_result_key: {
                                    'review_request' : NameArray(None,None,review_request_xml),
                                    'reviews ' : NameArray(None,"review",review_xml),
            }
        }
    
    def get_object(self, request, local_site_name=None, *args, **kwargs):
        review_request_id = kwargs.get('id')
        return review_request_resource.get_object(request, review_request_id, local_site_name, *args, **kwargs)


    def build_review(self, request, review):
        review_array = []
 
        review_array.append(NameArray("user",None,[review.user.username]))

        text_reviews = self.build_text_review(review) #adds text reviews
        if text_reviews is not None:
            review_array.append(text_reviews)

        code_reviews = review_array.append(self.build_code_review(request, review)) #adds code reviews
        if code_reviews is not None:
            review_array.append(code_reviews)

        screenshots_reviews = self.build_screenshot_review(review) #adds screenshot reviews
        if screenshots_reviews is not None:
            review_array.append(screenshots_reviews)
       
        if len(review_array):
            return NameArray(None,None,review_array)
        return None


    def build_text_review(self, review):

        text_review_array = []
        if review.body_top is not u'':
            text_review_array.append(NameArray(None,"text",[review.body_top]))

        review_replies = []
        for reply in review.public_replies():
            single_reply = []
            single_reply.append(NameArray(None,"user",[reply.user.username]))
            single_reply.append(NameArray(None,"comment",[reply.body_top]))
            review_replies.append(NameArray(None,None,single_reply))

        if len(review_replies):
            text_review_array.append(NameArray("replies","reply",review_replies)) 

        if len(text_review_array):
            return NameArray("text_review",None,text_review_array)

        return None


    def build_screenshot_review(self, review):       
        screenshot_review_array = []

        for screenshot in review.screenshot_comments.all():        

            screenshot_node = [] # Write SS Info
            screenshot_node.append(NameArray("url",None,[screenshot.get_image_url()]))
            screenshot_node.append(NameArray("text",None,[screenshot.text]))

            screenshot_replies = self.get_reply_comment(screenshot.public_replies()) # get replies      
            if len(screenshot_replies):
                screenshot_node.append(NameArray("replies","reply",screenshot_replies))

            screenshot_review_array.append(NameArray("screenshot_review",None,screenshot_node))
        
        if len(screenshot_review_array):
            return NameArray("screenshot_reviews",None,screenshot_review_array)
        return None


    def build_code_review(self, request,review):
        code_review_array = []

        context = RequestContext(request, {
                    'review_request': request,
                    'review': review,
                    })

        code_comments = review.comments.all()
        for code_comment in code_comments:

            content = list(get_file_chunks_in_range(context,
                            code_comment.filediff,
                            code_comment.interfilediff,
                            code_comment.first_line,
                            code_comment.num_lines,
                            False)) 

            code_node = [] #write code-review info                                          
            code_node.append(NameArray("text",None,[code_comment.text]))
            code_node.append(NameArray("type",None,[content[0]['change']]))
            code_node.append(NameArray("file",None,[code_comment.filediff.source_file]))
            code_node.append(NameArray("before",None,[content[0]['lines'][0][2]]))
            code_node.append(NameArray("after",None,[content[0]['lines'][0][5]]))
       
            code_replies = self.get_reply_comment(code_comment.public_replies()) # get replies                 
            if len(code_replies):
                code_node.append(NameArray("replies","reply",code_replies))
        
            code_review_array.append(NameArray("code_review",None,code_node))

        if  len(code_review_array):
            return NameArray("code_reviews",None,code_review_array)

        return None


    def get_reply_comment(self, public_replies):
        replies = []
        for reply in public_replies:
            inner_code_reply = []
            inner_code_reply.append(NameArray(None,"user",[reply.review.get().user.username]))
            inner_code_reply.append(NameArray(None,"comment",[reply.text]))
            replies.append(NameArray(None,None,inner_code_reply))
        return replies

reviewing_session_resource = ReviewRequestResource()


