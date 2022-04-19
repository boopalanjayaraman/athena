class ConditionToken:
  def __init__(self, condition_token, item_index, item_prefix, condition_str_operator_dict, condition_str_variable_dict):
    self.condition_token = condition_token
    self.item_index = item_index
    self.condition_str = ''
    self.condition_variable_str_format = '{}{}.{}'
    self.item_prefix = item_prefix
    self.condition_str_variable_dict = condition_str_variable_dict
    self.condition_str_operator_dict = condition_str_operator_dict

  def get_string(self) -> str:
    #process condition strings
    cond_tokens = self.condition_token.split(' ')

    prev_token = ''

    for c_token in cond_tokens:
      trimmed = str.strip(c_token)
      if  trimmed == 'CONDITION':
        continue
      elif trimmed == 'any':
        self.condition_str = ""
        break
      elif trimmed in self.condition_str_operator_dict:
        self.condition_str += self.condition_str_operator_dict[trimmed]  
      elif trimmed in self.condition_str_variable_dict:
        self.condition_str += str.format(self.condition_variable_str_format, self.item_prefix, self.item_index, trimmed)  
      else:
        self.condition_str += trimmed  

      prev_token = trimmed

    final_str = str.format("({})", self.condition_str) if str.strip(self.condition_str) != '' else ''

    return final_str