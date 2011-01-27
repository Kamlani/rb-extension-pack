# Reports extension for Review Board.�
from reviewboard.extensions.base impo�rt Extension
from reviewboard.extensions.hooks import ReviewRequestActionHook


class RBXMLExportActionHook(ReviewRequestActionHook):
    def get_action_info(self, context):
       return {'label':'XML Export','uri':'templates/rbxmlexport/test.txt'}
    
            
               


class RBXMLExport(Extension):
    is_configurable = False
    def __init__(self):
        Extension.__init__(self)
        self.rr_action_hook = RBXMLExportActionHook(self)
    
