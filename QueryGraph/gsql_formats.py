
SELECT_FORMAT_DEGREE1 = """
INTERPRET QUERY () FOR GRAPH {} {{
ListAccum <EDGE> @@edges;
t1 = {} 
    ACCUM @@edges += {};
PRINT @@edges;
PRINT t1;
}}
"""

SELECT_COUNT_FORMAT_DEGREE1 = """
INTERPRET QUERY () FOR GRAPH {} {{
SumAccum <EDGE> @@edges;
t1 = {} 
    ACCUM @@edges += 1;
PRINT @@edges;
PRINT t1;
}}
"""

SELECT_FORMAT_DEGREE2 = """
INTERPRET QUERY () FOR GRAPH {} {{
ListAccum <EDGE> @@edges;
t1 = {}
t2 = {}
    ACCUM @@edges += {};
PRINT @@edges;
PRINT t2;
}}
"""

SELECT_COUNT_FORMAT_DEGREE2 = """
INTERPRET QUERY () FOR GRAPH {} {{
SumAccum <EDGE> @@edges;
t1 = {}
t2 = {}
    ACCUM @@edges += 1;
PRINT @@edges;
PRINT t2;
}}
"""

SELECT_FORMAT_DEGREE3 = """
INTERPRET QUERY () FOR GRAPH {} {{
ListAccum <EDGE> @@edges;
t1 = {}
t2 = {}
t3 = {}
    ACCUM @@edges += {};
PRINT @@edges;
PRINT t3;
}}
"""

SELECT_COUNT_FORMAT_DEGREE3 = """
INTERPRET QUERY () FOR GRAPH {} {{
SumAccum <EDGE> @@edges;
t1 = {}
t2 = {}
t3 = {}
    ACCUM @@edges += 1;
PRINT @@edges;
PRINT t3;
}}
"""

SELECT_FORMAT_BASIC = """
 SELECT {} FROM {} 
"""

WHERE_FORMAT_BASIC = """
 WHERE {} 
"""


gsql_format_degree_mapping = {
    1 : {'select' : SELECT_FORMAT_DEGREE1, 'count': SELECT_COUNT_FORMAT_DEGREE1},
    2 : {'select' : SELECT_FORMAT_DEGREE2, 'count': SELECT_COUNT_FORMAT_DEGREE2},
    3 : {'select' : SELECT_FORMAT_DEGREE3, 'count': SELECT_COUNT_FORMAT_DEGREE3}
}