import datetime

class SpecialCasesHandler:

    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config

    def handle_parameters(self, param_dict : dict):
        '''
        takes the param dictionary as input and handles the tokens
        '''
        for key in param_dict.keys():
            if key.startswith('{YEAR'):
                self.check_and_handle_year(key, param_dict)

    def check_and_handle_year(self, key, param_dict):
        value = param_dict[key]
        new_year_value = self.get_new_year_value(value)
        if new_year_value != None:
            param_dict[key] = new_year_value
    
    def get_new_year_value(self, value):
        current_year = datetime.datetime.now().year

        if value == 'now':
            return current_year
        elif int(value) < 0:
            return current_year + int(value)
        else:
            return None
    
    