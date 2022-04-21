import datetime
import re
from xmlrpc.client import Boolean

class SpecialCasesHandler:

    year_now_condition_regex = 'year\s?=\s?(now)\s?'
    year_ago_condition_regex = 'year\s?=\s?(-\d+)\s?'
    year_ago_and_before_condition_regex = 'year\s?<=\s?(-\d+)\s?'

    year_special_cases_patterns = [ {'search_pattern' :year_now_condition_regex, 'replace_pattern': 'year = {}'}, {'search_pattern' :year_ago_condition_regex, 'replace_pattern': 'year = {}'}, {'search_pattern' :year_ago_and_before_condition_regex, 'replace_pattern': 'year <= {}'}]

    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config

    def handle_special_case_condition(condition_text):
        '''
        takes the condition_text and handles the year-related special cases in intermediate language (such as year= now, year = -1, etc)
        '''
        if ' year ' in str.lower(condition_text):
            return SpecialCasesHandler.check_and_handle_year(condition_text)
        else:
            return condition_text


    def check_and_handle_year(condition_text):
        for pattern in SpecialCasesHandler.year_special_cases_patterns:
            #check if the pattern is applicable --> if it is (year=now) or (year=-1) etc
            for search_match in re.finditer(pattern['search_pattern'], condition_text):
                value = search_match.group(1)
                new_year_value = SpecialCasesHandler.get_new_year_value(value)
                start = search_match.start()
                end = search_match.end()
                replace_text = str.format(pattern['replace_pattern'], new_year_value)
                if condition_text[start] == ' ': # a space
                    replace_text = ' ' + replace_text
                if end != len(condition_text) and condition_text[end] == ' ': # a space
                    replace_text = replace_text + ' '
                #replace condition
                condition_text = condition_text[:start] + replace_text + condition_text[end:]
        
        return condition_text
        
    
    def get_new_year_value(value):
        current_year = datetime.datetime.now().year

        if value == 'now':
            return current_year
        elif SpecialCasesHandler.is_int(value) and int(value) < 0:
            return current_year + int(value)
        else:
            return None
    
    
    def is_int(value : str) -> Boolean:
        try:
            v = int(value)
            return True
        except:
            return False