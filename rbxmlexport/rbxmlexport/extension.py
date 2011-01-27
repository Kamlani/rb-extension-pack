# Reports extension for Review Board.
from reviewboard.extensions.base import Extension


class RBXMLExport(Extension):
    is_configurable = False

    def __init__(self):
        Extension.__init__(self)
