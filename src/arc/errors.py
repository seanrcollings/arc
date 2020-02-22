class ConversionError(Exception):
    '''Generalized Conversion error if a conversion failes for some reason'''
    def __init__(self, value, convert_to, helper_text=None):
        '''
            :paraam value: the value attempting to be converted
            :convert_to: the type that the value was trying to converted to
            :helper_text: any additional helper text for the user
        '''
        super().__init__()
        self.value = value
        self.convert_to = convert_to
        self.helper_text = helper_text
