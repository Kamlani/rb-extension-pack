from reviewboard.reviews.views import get_file_chunks_in_range
from djblets.webapi.core import NameArray
from django.template.context import RequestContext
from reviewboard.reviews.models import ReviewRequest
from reviewboard.webapi.resources import review_request_resource
from django.conf import settings
from django.contrib.sites.models import Site
from reviewboard.webapi.resources import WebAPIResource

class ReviewRequestResource(WebAPIResource):
    model = ReviewRequest
    name = 'review-request'
    plural_name = 'review-requests'
    allowed_methods = ('GET')
    uri_object_key = 'id'
    fields = ('id')

    def get(self, request, *args, **kwargs):
        my_review_request = self.get_object(request, *args, **kwargs)

        review_request_xml = [] #Review-Request xml info
        if my_review_request.submitter.username:
            review_request_xml.append(NameArray(
                "user",
                None,
                [my_review_request.submitter.username]))
        if my_review_request.summary:
            review_request_xml.append(NameArray(
                "summary",
                None,
                [my_review_request.summary]))
        if my_review_request.description:
            review_request_xml.append(NameArray(
                "description",
                None,
                [my_review_request.description]))
        if my_review_request.testing_done:
            review_request_xml.append(NameArray(
                "testing",
                None,
                [my_review_request.testing_done]))
        if my_review_request.changenum:
            review_request_xml.append(NameArray(
                "changenum",
                None,
                [my_review_request.changenum]))
        if my_review_request.bugs_closed:
            review_request_xml.append(NameArray(
                "bugs",
                None,
                [my_review_request.bugs_closed]))
        if my_review_request.branch:
            review_request_xml.append(NameArray(
                "branch",
                None,
                [my_review_request.branch]))

        people_array = []
        for person in my_review_request.target_people.all():
            people_array.append(NameArray(
                "user",
                None,
                [person.username]))
        if len(people_array):
            review_request_xml.append(NameArray(
                "people",
                None,
                people_array))

        group_array = []
        for group in my_review_request.target_groups.all():
            people_array.append(NameArray(
                "user",
                None,
                [group.display_name]))

        if len(group_array): 
            review_request_xml.append(NameArray(
                "group",
                None,
                group_array))

        review_xml = []
        for review in my_review_request.get_public_reviews():
            current_review = self.build_review(request,review)
            if current_review: review_xml.append(current_review)

        return 200, {
            self.item_result_key: {
                            'request': NameArray(None,None,review_request_xml),
                            'reviews ': NameArray(None,"review",review_xml),
                            }
                    }

    def get_object(self, request, local_site_name=None, *args, **kwargs):
        review_request_id = kwargs.get('id')
        return review_request_resource.get_object(
                request,
                review_request_id,
                local_site_name,
                *args,
                **kwargs)

    # Builds the entire review, calls build_bodytop(self, review)
    # build_body_top_screenshot(self, review) and
    # build_body_top_diffs(self, request, review)
    def build_review(self, request, review):
        review_array = []

        review_array.append(NameArray(
            "user",
            None,
            [review.user.username]))

        # Handle body_top reviews
        body_top = self.build_body_top(review) # adds body_top text review part
        if body_top is not None:
            review_array.append(body_top)

        # Handle screenshots and diffs
        body_code_screenshot = []
        body_code = self.build_diffs(request, review)
        body_screenshot = self.build_screenshots(review)

        if body_code is not None:
            body_code_screenshot.extend(body_bottom_code)
        if body_screenshot is not None:
            body_code_screenshot.extend(body_bottom_screenshot)

        if len(body_code_screenshot):
            review_array.append(NameArray(
                "comments",
                None,
                body_code_screenshot))

        # Return review in a NameArray
        if len(review_array):
            return NameArray(
                None,
                None,
                review_array)

        return None

    # Adds part of a review that contain just the body_top text
    # along with the associated replies
    def build_body_top(self, review):

        text_review_array = []
        if review.body_top is not u'':
            if review.body_top == "Ship It!":
                return(NameArray(
                    "ship-it",
                    None,
                    ["1"]))
            else:
                text_review_array.append(NameArray(
                    None,
                    "text",
                    [review.body_top]))

        review_replies = []
        for reply in review.public_replies():
            single_reply = []
            if reply.body_top is not u'':
                single_reply.append(NameArray(
                    None,
                    "user",
                    [reply.user.username]))
                single_reply.append(NameArray(
                    None,
                    "comment",
                    [reply.body_top]))
                review_replies.append(NameArray(
                    None,
                    None,
                    single_reply))

        if len(review_replies):
            text_review_array.append(NameArray(
                "replies",
                "reply",
                review_replies))

        if len(text_review_array):
            return NameArray(
                "body-top",
                None,
                text_review_array)

        return None

    # Adds part of a review that contains a screenshot review
    # along with the associated replies
    def build_body_top_screenshot(self, review):
        screenshot_review_array = []

        for screenshot in review.screenshot_comments.all():

            screenshot_node = [] # Write SS Info
            screenshot_node.append(NameArray(
                "type",
                None,
                ["screenshot"]))
            screenshot_node.append(NameArray(
                "url",
                None,
                ["http://" +
                    Site.objects.get_current().domain +
                    screenshot.get_image_url()]))
            screenshot_node.append(NameArray(
                "text",
                None,
                [screenshot.text]))

            screenshot_replies = self.get_reply_comment(
                    screenshot.public_replies())

            if len(screenshot_replies):
                screenshot_node.append(NameArray(
                    "replies",
                    "reply",
                    screenshot_replies))

            screenshot_review_array.append(NameArray(
                "comment",
                None,
                screenshot_node))

        if len(screenshot_review_array):
            return screenshot_review_array

        return None

    # Adds part of a review that contains a code/diff review
    # along with the associated replies
    def build_body_top_diffs(self, request,review):
        diff_review_array = []

        context = RequestContext(request, {
                    'review_request': request,
                    'review': review,
                    })

        diff_comments = review.comments.all()
        for diff_comment in diff_comments:

            content = list(get_file_chunks_in_range(context,
                            diff_comment.filediff,
                            diff_comment.interfilediff,
                            diff_comment.first_line,
                            diff_comment.num_lines,
                            False))

            diff_node = [] #write code-review info
            diff_node.append(NameArray(
                    "type",
                    None,
                    ["diff"]))
            diff_node.append(NameArray(
                "text",
                    None,
                    [diff_comment.text]))
            diff_node.append(NameArray(
                    "file",
                    None,
                    [diff_comment.filediff.source_file]))

            chunks = []
            for single_line in content[0]['lines']:
                chunk = []
                chunk.append(NameArray(
                    "linenum",
                    None,
                    [single_line[0]]))
                chunk.append(NameArray(
                    "before",
                    None,
                    [single_line[2]]))
                chunk.append(NameArray(
                    "after",
                    None,
                    [single_line[5]]))
                chunks.append(NameArray(
                    "line",
                    None,
                    chunk))

            diff_node.append(NameArray("chunk",
                    None,
                    chunks))
            diff_replies = self.get_reply_comment(
                    diff_comment.public_replies())

            if len(diff_replies):
                diff_node.append(NameArray(
                    "replies",
                    "reply",
                    diff_replies))

            diff_review_array.append(NameArray(
                    "comment",
                    None,
                    diff_node))

        if  len(diff_review_array):
            return diff_review_array

        return None

    # Helper function that gets the replies of a review
    def get_reply_comment(self, public_replies):
        replies = []
        for reply in public_replies:
            reply_array = []
            reply_array.append(NameArray(
                None,
                "user",
                [reply.review.get().user.username]))
            reply_array.append(NameArray(
                None,
                "comment",
                [reply.text]))
            replies.append(NameArray(
                None,
                None,
                reply_array))
        return replies

reviewing_session_resource = ReviewRequestResource()
