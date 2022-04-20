# Athena

Project Athena is a prototype for an automatic knowledge graph framework that uses NLP based querying to query the graph.  Built as part of the TigerGraph Graph-for-all challenge.

In one sentence, Athena aims to be a generic knowledge graph, that builds itself, speaks your language and blends with existing tools.

### Project Structure

- **GenerateGraph** is the graph builder program based on python. It runs on top of unstructured textual data, extracts entities and relationships between them and creates the graph automatically. It uses BERT for entity extraction, Spacy for POS tagging. It uses pattern matching to filter the text that has a pattern of relationship between two entities or objects or locations or persons.

When this runs on a dataset, it first tries to understand the most frequently used domain verbs and nouns. To save time, this can be stored to a local file and can be used on subsequent runs of the same dataset. These files are available as ```domain_nouns_list.json``` and ```domain_verbs_list.json```

The necessary datasets to run this quickly and test are available under the ```data``` folder. The ```raw_partner_headlines_micro.csv``` contains just 10 rows (used for quick debugging, to check if everything is ok). The ```raw_partner_headlines_micro.csv``` contains 100 rows. The ```raw_partner_headlines_small.csv``` contains just 200000 rows for moderate level of testing. The input dataset file can be specified as part of the configuration file.

The original dataset used for testing contained close to 1 million rows (1000000+). This is available in a separate google drive link.

```domain_words_extractor.py``` contains the logic to extract most frequently used verbs (relationships) and nouns (objects) by a dataset. The degree of frequency can be controlled by a configuration setting. If we mention 0.7, that means 70% of the most frequently used verbs / nouns will be used for creating relationships and objects. This is important to know because any other word apart from the domain words will be skipped during relationship creation or object entity creation.

```entity_extractor.py``` contains the logic to extract entities. Uses BERT.
```input_data_handler.py``` is the entry point to execution. Fetches the input data and controls the flow of the program.
```pos_extractor.py``` contains the logic to do the POS (parts of speech) tagging on a given sentence. This is responsible to extract verbs and thus the relationships.
```graph_generator.py``` handles the operations with TigerGraph. Configuration settings to govern this are available in the configuration file.
```pattern_finder.py``` matches the sentences after entity extraction and pos tagging to check if they meet the acceptable pattern for graph creation. For ex., for proper creation of relationships and nodes in the graph, the sentences need to be in acceptable formats like Entity-Verb-Entity/Noun or Entity-Verb-Entity-Entity-Entity. There can be more such formats, but for this prototype, we stick to a few.

- **Nlp2Gsql** is a seq2seq RNN model written using PyTorch helping translate between NLP questions to GSQL queries. It uses a hand-made dataset that has mappings between plain natural language queries and 'intermediate language' sequences for training. The intermediate language sequences can be further converted to GSQL.

The prototype Jupyter Notebook can be found under ```prototype``` folder. The ```sequence.py``` is a representative class denoting input and output sequences. 

The ```training_pipeline.py``` is the entry point to training execution and it controls the flow. 

 ```encoder_rnn.py``` and ```attention_decoder_rnn.py``` are encoder and attention decoder classes respectively. ```seq2seq_rnn.py``` is where the training happens. It trains the model on top of the data, saves them to local folders. The saved models can be found under ```saved_models``` folder. For evaluation (model inference), these models can be loaded back and evaluated.

- **QueryGraph** is a flask service that takes in the user input (Natural language question), parameterizes it, and converts it into closely resembling intermediate language output using the seq2seq RNN model above. After that, it parses and converts the output into a relevant GSQL string. The GSQL is executed against the TigerGraph database and data are fetched.

This folder contains some of the files from the above two modules as well. 

The ```query_pipeline.py``` is the entry point for the whole execution and controls the flow of the program. 

```parameter_tokenizer.py``` parameterizes the input natural langauge query and prepares it to be sent to seq2seq model. For ex., a question like the below:

```who has bought Agilent Technologies Inc between the dates 2014-04-01 and 2014-08-01``` (NOTE: it is important that the dates have to be in yyyy-mm-dd format for the prototype)

will get parameterized to the below:

```who has {VERB} {ORGANIZATION} between the dates {DATE1} and {DATE2}```

which further will get translated into:

```VERTEX any | CONDITION any | EDGE {VERB} | CONDITION happened >= {DATE1} AND happened <= {DATE2} | VERTEX Organization | CONDITION name = {ORGANIZATION}```

by the seq2seq model. 

```gsql_converter.py``` and ```gsql_formats.py``` are used to convert the above intermediate language format into a GSQL query. ```vertex_token.py ```, ```edge_token.py``` and  ```condition_token.py``` are used to represent the tokens (split by '|' in the above intermediate language sentence) and they convert themselves to respective GSQL parts. ```graph_connector.py``` executes the GSQL query against TigerGraph.








