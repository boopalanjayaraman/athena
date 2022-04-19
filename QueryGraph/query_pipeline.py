
from graph_connector import GraphConnector
from gsql_converter import GsqlConverter
from training_pipeline import TrainingPipeline
from parameter_tokenizer import ParameterTokenizer
from pos_extractor import PosExtractor
from entity_extractor import EntityExtractor
import json

class QueryPipeline:

    def __init__(self, logger, config, parameter_tokenizer : ParameterTokenizer, seq2seq_pipeline : TrainingPipeline, gsql_converter : GsqlConverter, graph_connector: GraphConnector) -> None:
        self.logger = logger
        self.config = config
        self.parameter_tokenizer = parameter_tokenizer
        self.seq2seq_pipeline = seq2seq_pipeline
        self.gsql_converter = gsql_converter
        self.graph_connector = graph_connector

        self.logger.info('Initialized QueryPipeline.')

    def process_nlp_query(self, query):

        #get the parameterized nlp query for converting to intermediate language
        question_content, params_dict = self.parameter_tokenizer.parameterize(query)

        #pass the parameterized nlp query into seq2seq and get the intermediate language (il)
        il = self.seq2seq_pipeline.evaluate_saved_model(question_content)

        #pass the intermediate language to convert that into gsql
        gsql = self.gsql_converter.get_gsql(il)

        #replace the parameters through param_dict
        for key in params_dict.keys():
            if key in gsql:
                gsql = gsql.replace(key, params_dict[key])

        #pass the gsql to graph connector to run the query and get the results
        result = self.graph_connector.run_gsql(gsql=gsql)
        result_obj = {}
        try:
            #conver to json
            result_obj = json.loads(result)
            result_obj = { 'results': result_obj['results'] }
        except Exception as ex:
            self.logger.info(str.format("Error processing NLP query {}.", query))
            self.logger.error('Error:', exc_info=ex)
            self.logger.info(str.format("Result from gsql execution: {}.", result))
            result_obj['results'] = {'error': result}
        #return the result in json
        return result_obj





       
 