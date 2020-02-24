class ArcError(Exception):
    '''Base Arc Exception'''


class ExecutionError(ArcError):
    '''Raised if there is a problem during the execution of a script'''


class ConversionError(ArcError):
    '''Raised if a type conversion fails '''
    def __init__(self, value, convert_to, helper_text=None):
        ''' Initializes the conversion errors
        :paraam value: the value attempting to be converted
        :convert_to: the type that the value was trying to converted to
        :helper_text: any additional helper text for the user
        '''
        super().__init__()
        self.value = value
        self.convert_to = convert_to
        self.helper_text = helper_text
