# Athena

Project Athena is a prototype for an automatic knowledge graph framework that uses NLP based querying to query the graph.  Built as part of the TigerGraph Graph-for-all challenge.

In one sentence, Athena aims to be a generic knowledge graph, that builds itself, speaks your language and blends with existing tools.

## Project Structure

### GenerateGraph

**GenerateGraph** is the graph builder program based on python. It runs on top of unstructured textual data, extracts entities and relationships between them and creates the graph automatically. It uses BERT for entity extraction, Spacy for POS tagging. It uses pattern matching to filter the text that has a pattern of relationship between two entities or objects or locations or persons.

When this runs on a dataset, it first tries to understand the most frequently used domain verbs and nouns. To save time, this can be stored to a local file and can be used on subsequent runs of the same dataset. These files are available as ```domain_nouns_list.json``` and ```domain_verbs_list.json```

The necessary datasets to run this quickly and test are available under the ```data``` folder. The ```raw_partner_headlines_micro.csv``` contains just 10 rows (used for quick debugging, to check if everything is ok). The ```raw_partner_headlines_micro.csv``` contains 100 rows. The ```raw_partner_headlines_small.csv``` contains just 200000 rows for moderate level of testing. The input dataset file can be specified as part of the configuration file.

The original dataset used for testing contained close to 1 million rows (1000000+). This is available in a separate google drive link.

```domain_words_extractor.py``` contains the logic to extract most frequently used verbs (relationships) and nouns (objects) by a dataset. The degree of frequency can be controlled by a configuration setting. If we mention 0.7, that means 70% of the most frequently used verbs / nouns will be used for creating relationships and objects. This is important to know because any other word apart from the domain words will be skipped during relationship creation or object entity creation.

```entity_extractor.py``` contains the logic to extract entities. Uses BERT.
```input_data_handler.py``` is the entry point to execution. Fetches the input data and controls the flow of the program.
```pos_extractor.py``` contains the logic to do the POS (parts of speech) tagging on a given sentence. This is responsible to extract verbs and thus the relationships.
```graph_generator.py``` handles the operations with TigerGraph. Configuration settings to govern this are available in the configuration file.
```pattern_finder.py``` matches the sentences after entity extraction and pos tagging to check if they meet the acceptable pattern for graph creation. For ex., for proper creation of relationships and nodes in the graph, the sentences need to be in acceptable formats like Entity-Verb-Entity/Noun or Entity-Verb-Entity-Entity-Entity. There can be more such formats, but for this prototype, we stick to a few.

### Nlp2Gsql

**Nlp2Gsql** is a seq2seq RNN model written using PyTorch helping translate between NLP questions to GSQL queries. It uses a hand-made dataset that has mappings between plain natural language queries and 'intermediate language' sequences for training. The intermediate language sequences can be further converted to GSQL.

The prototype Jupyter Notebook can be found under ```prototype``` folder. The ```sequence.py``` is a representative class denoting input and output sequences. 

The ```training_pipeline.py``` is the entry point to training execution and it controls the flow. 

 ```encoder_rnn.py``` and ```attention_decoder_rnn.py``` are encoder and attention decoder classes respectively. ```seq2seq_rnn.py``` is where the training happens. It trains the model on top of the data, saves them to local folders. The saved models can be found under ```saved_models``` folder. For evaluation (model inference), these models can be loaded back and evaluated.

### QueryGraph

**QueryGraph** is a flask service that takes in the user input (Natural language question), parameterizes it, and converts it into closely resembling intermediate language output using the seq2seq RNN model above. After that, it parses and converts the output into a relevant GSQL string. The GSQL is executed against the TigerGraph database and data are fetched.

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

### PrototypeNotebooks

PrototypeNotebooks folder contain the Jupyter Notebooks which in turn has the prototypes created during the feasibility phase of the project.

## Configuring and Executing the programs

## Prerequisites

Install ```Anaconda Python```. And, from the anaconda python shell prompt, install the following libraries. (Most of the commands are based on windows environment. Please do the equivalent, if you are using a linux environment.)

    pip install setuptools
    pip install numpy
    pip install pandas
    pip install spacy
    pip install transformers
    pip install nltk

```conda init powershell``` (from admin powershell)

If you encounter the following error in when you open the powershell window - ```\WindowsPowerShell\profile.ps1 cannot be loaded because running scripts is disabled on this system``` then run the following command and restart the powershell window.

    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned

Then install the following

    pip install transformers
    pip install tokenizers

**To install spacy**

    python -m spacy download en_core_web_sm

Or if you want to install using conda

    conda install -c conda-forge spacy

and then, 

    python -m spacy download en

If the above solutions did not work, then we can download the spacy package and manually install it from a local folder.
Download the package from https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.0.0/en_core_web_sm-3.0.0.tar.gz and install the package using the following command (admin mode powershell)

    pip install en_core_web_sm-3.0.0.tar.gz


### GenerateGraph

Please open the workspace folder using Visual Studio Code. Select the Launch configuration "Python: Generate Graph" in ```launch.json`` and start debugging. 

```[GeneralSettings]```

```LoadBERTFromLocal = True``` To save time from importing the BERT library and models, we can download it to a local folder and import it from from there. Set to False if you want to rather import the BERT directly from the remote branch. 

```LocalBERTPath = D:/Boopalan/Graph/athena/GenerateGraph/dslim/bert-base-NER ``` (The path is only indicative). Set it to your local folder path that contains the BERT repository and saved models. Takes effect only if ```LoadBERTFromLocal``` is set to ```True```

```RemoteBERTPath = dslim/bert-base-NER``` Takes effect only if ```LoadBERTFromLocal``` is set to ```False```

```DumpDomainWordLists = True``` Setting it to True makes the domain words extractor class to save the domain words into files (configured by ```DomainVerbListPath``` and ```DomainNounListPath``` below)  to save time in the subsequent runs. 

```PreloadDomainWordLists = True``` If set to True, loads the domain words from the below mentioned file paths to save time in the executions.

```DomainVerbListPath = domain_verbs_list.json``` When ```PreloadDomainWordLists``` is set to ```True```, the domain verbs list is loaded from here rather than going over the full dataset and computing it again. A version is already available in the repo for the sample full dataset.

```DomainNounListPath = domain_nouns_list.json``` When ```PreloadDomainWordLists``` is set to ```True```, the domain verbs list is loaded from here rather than going over the full dataset and computing it again.


```[GraphSettings]```

```SentencePatternRegex = E+V[EN]+``` Indicates the acceptable pattern of sentences that are eligible for graph relationships creation. Only sentences that satisfy this pattern will be used for creating nodes and relationships. E - denotes an entity (Organization, Location, Person, Object), V - denotes a Verb (found in the domain verbs list), N - denotes a noun (found in the domain nouns list)

```HostName = https://athena.i.tgcloud.io``` TigerGraph cloud host name
```UserName = tigergraph``` 
```Password = tigergraph``` 
```GraphName = athenagraph1304``` a graph name (either to be created newly or an existing one)
```CreateGraph = True``` When set to True, creates the graph (found in the graph name setting) if not exists.
```Secret = ``` If left blank, creates a secret and uses it. To save time between subsequent executions, we can create a secret and set it here.
```ApiToken = ``` If left blank, creates a new API token and uses it for calling TigerGraph API

```[InputDataSettings]```

```InputDataSetFile = data\raw_partner_headlines.csv``` the path of the input data set.
```ERConfidenceScore = 0.7``` used in entity recognition. Takes only those token classifications from BERT which have a confidence score of above 0.7. 
```ContentTitle = headline``` the title of column in the dataset that has the unstructured content
```DateTitle = date``` the title of column in the dataset that has the date

```CommonWordCoveragePercent = 0.7``` Indicates the degree of frequently used words in domain verbs and nouns. If we mention 0.7, that means 70% of the most frequently used verbs / nouns will be used for creating relationships and objects.

### Nlp2Gsql

Open the workspace folder using Visual Studio Code. Select the Launch configuration "Python: Train NLP 2 GSQL Intermediate" in ```launch.json`` and start debugging. 

```[ModelSettings]```

    MAX_VOCAB_SIZE = 30000
    MIN_COUNT = 5
    MAX_SEQUENCE_LENGTH = 20
    BATCH_SIZE = 64
    MAX_LENGTH = 50
    Hidden_Size = 256
    Iterations = 20000
    Print_Every = 1000
    Dropout = 0.1
    Encoder_Model_file = saved_models\encoder1-model.pt
    Attention_Decoder_Model_file = saved_models\attn_decoder1-model.pt

```[InputDataSettings]```
    InputDataSetFile = dataset\NLP Seq2Seq DataSet 3 Final.csv

The above settings are seq2seq model training configurations, and are mostly self-explanatory. You can increase or decrease Batch Size or Max length or Training Iterations. The encoder model and attention decoder models will be saved to the file path mentioned in the relevant configurations

### QueryGraph

Open the workspace folder using Visual Studio Code. Select the Launch configuration "Python: Run NLP Query Service" in ```launch.json`` and start debugging.

The sections ```[ModelSettings]```, ```[InputDataSettings]```, ```[GraphSettings]```, ```[GeneralSettings]``` and their configurations here are same as in the previous two modules. Please make sure they are set to the same values in both the places.




