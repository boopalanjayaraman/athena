
from pos_extractor import PosExtractor
from entity_extractor import EntityExtractor
import re

class ParameterTokenizer:

    year_regex = "(?:before)?(?:after)?(?:in)?(?:between)?(?:Year)?(?:YEAR)?(?:year)?(?:s)?\d\d\d\d\s"
    date_regex = "\d\d\d\d[/-]\d\d[/-]\d\d"

    def __init__(self, logger, config, entity_extractor : EntityExtractor, pos_extractor : PosExtractor) -> None:
        self.logger = logger
        self.config = config
        self.entity_extractor = entity_extractor
        self.pos_extractor = pos_extractor
        self.logger.info('Initialized ParameterTokenizer.')

    def parameterize(self, query):
        self.logger.info("ParameterTokenizer: parameterize method is called")
        params_dict = {}
        question_content = query
        #parameterizing the entities first
        question_content, params_dict = self.parameterize_entities(question_content, params_dict)
        #parameterizing the verbs
        question_content, params_dict = self.parameterize_verbs(question_content, params_dict)
        #parameterizing the dates
        question_content, params_dict = self.parameterize_dates(question_content, params_dict)
        #parameterizing the years
        question_content, params_dict = self.parameterize_years(question_content, params_dict)

        ## TODO: handle year special cases - "5 years ago", etc.

        return question_content, params_dict


    def parameterize_entities(self, question_content, params_dict):
        # fetch and parameterize entities - organization, location and person
        entities = self.entity_extractor.get_entities_bert(question_content)

        orgs_count = 0
        objs_count = 0
        locs_count = 0
        pers_count = 0

        organization_suffix = 'ORGANIZATION'
        object_suffix = 'OBJECT'
        person_suffix = 'PERSON'
        location_suffix = 'LOCATION'

        for entity in entities:
            entity_type = entity['entity']
            if entity_type == 'I-ORG' or entity_type == 'B-ORG':
                orgs_count += 1
            elif entity_type == 'I-PER' or entity_type == 'B-PER':
                pers_count += 1
            elif entity_type == 'I-LOC' or entity_type == 'B-LOC':
                locs_count += 1
            elif entity_type == 'I-MISC' or entity_type == 'B-MISC':
                objs_count += 1

        org_index = 0
        loc_index = 0
        pers_index = 0

        index_offset = 0

        for entity in entities:
            entity_type = entity['entity']
            replace_token = ''
            if entity_type == 'I-ORG' or entity_type == 'B-ORG':
                if orgs_count > 1:
                    org_index += 1
                    replace_token = str.format("{{{} {}}}", organization_suffix, org_index)
                else:
                    replace_token = str.format("{{{}}}", organization_suffix)

            elif entity_type == 'I-PER' or entity_type == 'B-PER':
                if pers_count > 1:
                    pers_index += 1
                    replace_token = str.format("{{{} {}}}", person_suffix, pers_index)
                else:
                    replace_token = str.format("{{{}}}", person_suffix)

            elif entity_type == 'I-LOC' or entity_type == 'B-LOC':
                if locs_count > 1:
                    loc_index += 1
                    replace_token = str.format("{{{} {}}}", location_suffix, loc_index)
                else:
                    replace_token = str.format("{{{}}}", location_suffix)

            start_index = entity['startIndex'] - index_offset
            end_index = entity['startIndex'] - index_offset + len(entity['token'])
            question_content = question_content[:start_index] + replace_token + question_content[end_index:]
            index_offset = index_offset + (len(entity['token']) - len(replace_token))
            params_dict[replace_token] = str.format('"{}"', entity['token'])

        self.logger.info("parameterize_entities finished")
        self.logger.info(str.format("parameterized_entities string: {}", question_content))

        return question_content, params_dict


    def parameterize_verbs(self, question_content, params_dict):
        pos_tokens = self.pos_extractor.get_pos_sentence(question_content)

        verbs_count = 0
        verb_suffix = 'VERB'
        verb_index = 0

        index_offset = 0

        for pos in pos_tokens:
            if pos['pos'] == 'VERB':
                verbs_count += 1

        for pos in pos_tokens:
            replace_token = ''
            if pos['pos'] == 'VERB':
                if verbs_count > 1:
                    verb_index += 1
                    replace_token = str.format("{{{} {}}}", verb_suffix, verb_index)
                else:
                    replace_token = str.format("{{{}}}", verb_suffix)

                start_index = pos['index'] - index_offset
                end_index = pos['index'] - index_offset + len(pos['token'])
                question_content = question_content[:start_index] + replace_token + question_content[end_index:]
                index_offset = index_offset + (len(pos['token']) - len(replace_token))

                params_dict[replace_token] = "r_" + pos['lemma'] # this is important --> lemma

        self.logger.info("parameterize_verbs finished")
        self.logger.info(str.format("parameterized_verbs string: {}", question_content))

        return question_content, params_dict

    def parameterize_dates(self, question_content, params_dict):

        date_matches = re.split(ParameterTokenizer.date_regex, question_content)
        date_values = re.findall(ParameterTokenizer.date_regex, question_content)

        date_index = 0
        date_count = len(date_values)
        date_suffix = 'DATE'

        for index in range(len(date_matches) -1):
            replace_token = ''
            if date_count > 1:
                date_index += 1
                replace_token = str.format("{{{} {}}}", date_suffix, date_index)
            else:
                replace_token = str.format("{{{}}}", date_suffix)

            question_content +=  replace_token + date_matches[index+1]
            if index == len(date_matches) -1:
                break
            params_dict[replace_token] = str.format('"{}"', date_values[index])

        self.logger.info("parameterize_dates finished")
        self.logger.info(str.format("parameterized_dates string: {}", question_content))

        return question_content, params_dict


    def parameterize_years(self, question_content, params_dict):
        year_matches = re.split(ParameterTokenizer.year_regex, question_content)
        year_values = re.findall(ParameterTokenizer.year_regex, question_content)

        year_index = 0
        year_count = len(year_values)
        year_suffix = 'YEAR'

        for index in range(len(year_matches) -1):
            replace_token = ''
            if year_count > 1:
                year_index += 1
                replace_token = str.format("{{{} {}}}", year_suffix, year_index)
            else:
                replace_token = str.format("{{{}}}", year_suffix)

            next_match_string = year_matches[index+1] if year_matches[index+1].startswith(' ') else ' ' + year_matches[index+1]
            question_content +=  replace_token + next_match_string
            if index == len(year_matches) -1:
                break
            params_dict[replace_token] = str.strip(year_values[index])

        self.logger.info("parameterize_years finished")
        self.logger.info(str.format("parameterized_years string: {}", question_content))

        return question_content, params_dict

    
