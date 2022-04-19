from edge_token import EdgeToken
from vertex_token import VertexToken
from gsql_formats import *
from conditional_operator_variable_dict import *

class GsqlConverter:

    def __init__(self, logger, config) -> None:
        self.logger = logger
        self.config = config
        self.graph_name = config['GraphSettings']['GraphName']
        ## TODO: handle special cases - "OPERATION", etc.
        self.logger.info('Initialized GsqlConverter.')

    def get_gsql(self, il) -> str:
        gsql_dict, final_edge_alias = self.generate_gsql_from_intermediate_language(il)
        # get the format of gsql
        final_gsql_format = gsql_format_degree_mapping[len(gsql_dict.keys())]['select']

        gsql_strings = [ self.graph_name ]
        for index in range(len(gsql_dict.keys())):
            gsql_strings.append(gsql_dict['t'+str(index +1)])

        gsql_strings.append(final_edge_alias)
        final_gsql_without_params = str.format(final_gsql_format, *gsql_strings)
        ## TODO: handle special cases - "OPERATION COUNT", etc. here

        return final_gsql_without_params


    def generate_gsql_from_intermediate_language(self, il):
        """
        This method converts the parameterized intermediate language coming from the seq2seq model that converts plain NLP questions.
        intermediate language format samples - 
        --> VERTEX any | CONDITION any | EDGE {VERB1} | CONDITION any | VERTEX Organization | CONDITION any | EDGE {VERB2} |CONDITION any | VERTEX Organization | CONDITION name = {ORGANIZATION}
        --> VERTEX Person | CONDITION name = {PERSON} | EDGE any | CONDITION year >= {YEAR1} AND year <= {YEAR2} | VERTEX any | CONDITION any
        """
        il_tokens = il.split('|')

        conditions_stack = []
        units_stack = []

        for il_token in il_tokens:
            il_token = str.strip(il_token)
            if il_token.startswith('CONDITION'):
                conditions_stack.append(il_token)
            else:
                units_stack.append(il_token)

        item_index = 0

        staged_units = {} # has the subsets that are processed already (ex., first hop)
        current_units = [] # has the units that are being processed currently, will get reset.
        current_format = []
        units_aliases = []
        final_edge_alias = ''

        subset_index = 0

        for index in range(len(units_stack)):
            unit_token = units_stack[index]
            condition_token = conditions_stack[index]

            if unit_token.startswith('VERTEX'):
                vertex_token = VertexToken(unit_token, condition_token, item_index, condition_str_operator_dict, condition_str_variable_dict)
                output_str, condition_str, item_alias = vertex_token.get_string()
                current_format.append('V')
                current_units.append((output_str, condition_str)) #tuple
                units_aliases.append(item_alias)

            elif unit_token.startswith('EDGE'):
                edge_token = EdgeToken(unit_token, condition_token, item_index, condition_str_operator_dict, condition_str_variable_dict)
                output_str, condition_str, item_alias = edge_token.get_string()
                current_format.append('E')
                current_units.append((output_str, condition_str)) #tuple
                units_aliases.append(item_alias)
                final_edge_alias = item_alias

            if "".join(current_format) == 'VEV':
                #process here
                select_str = "-".join([unit[0] for unit in current_units])
                where_str = " AND ".join([unit[1] for unit in current_units if str.strip(unit[1]) != ''])

                select_str_full = str.format(SELECT_FORMAT_BASIC, units_aliases[0], select_str)
                where_str_full = str.format(WHERE_FORMAT_BASIC, where_str)

                select_str_full = select_str_full + (' ' + where_str_full if str.strip(where_str) != '' else '')

                subset_index +=1

                staged_units["t"+str(subset_index)] = select_str_full
                current_format = ['S']
                current_units = []

            elif "".join(current_format) == 'SEV':
                #process here
                select_str = "-".join([unit[0] for unit in current_units])
                where_str = " AND ".join([unit[1] for unit in current_units if str.strip(unit[1]) != ''])

                #select_str = "t"+str(subset_index) + "-" + select_str 
                subset_alias = str.format("s_t{}", str(subset_index))
                select_str = str.format("t{}:{}-{}",str(subset_index), subset_alias, select_str) #including the previous subset along with the newly processed nodes

                select_str_full = str.format(SELECT_FORMAT_BASIC, subset_alias, select_str)
                where_str_full = str.format(WHERE_FORMAT_BASIC, where_str)

                select_str_full = select_str_full + (' ' + where_str_full if str.strip(where_str) != '' else '')

                subset_index +=1

                staged_units["t"+str(subset_index)] = select_str_full
                current_format = ['S']
                current_units = []

            item_index += 1
        
        return staged_units, final_edge_alias