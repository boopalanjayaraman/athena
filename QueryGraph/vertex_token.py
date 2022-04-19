from condition_token import ConditionToken


class VertexToken:
  def __init__(self, unit_token, condition_token, item_index, condition_str_operator_dict, condition_str_variable_dict):
    self.unit_token = unit_token
    self.condition_token = condition_token
    self.item_index = item_index
    self.output_str = ''
    self.condition_str = ''
    self.output_str_format = "{}:{}{}"
    self.condition_str_format = ""
    self.prefix = 'v'
    self.item_alias_format = "{}{}"
    self.item_alias = ""
    self.condition_str_variable_dict = condition_str_variable_dict
    self.condition_str_operator_dict = condition_str_operator_dict

  def get_string(self) -> str:
    #process condition strings
    tokens = self.unit_token.split(' ')

    for token in tokens:
      trimmed = str.strip(token)
      if  trimmed == 'VERTEX':
        continue
      elif trimmed == 'any':
        self.output_str = str.format(self.output_str_format, "", self.prefix, self.item_index)
        self.item_alias = str.format(self.item_alias_format, self.prefix, self.item_index)
        break
      else:
        self.output_str = str.format(self.output_str_format, trimmed, self.prefix, self.item_index)
        self.item_alias = str.format(self.item_alias_format, self.prefix, self.item_index)

    #process condition strings
    condition_token = ConditionToken(self.condition_token, self.item_index, self.prefix,  self.condition_str_operator_dict, self.condition_str_variable_dict)
    self.condition_str = condition_token.get_string()

    return self.output_str, self.condition_str, self.item_alias