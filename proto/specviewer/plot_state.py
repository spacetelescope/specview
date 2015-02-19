class PlotState(object):
    '''Formalize plotting states'''

    def __init__(self):
        self.isvalid = False # Validity of plot.
        self.line = None

    # Plot validity
    def invalidate(self):
        self.isvalid = False
    def validate(self):
        self.isvalid = True
