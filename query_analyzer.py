'''
Module containing a single function used to determine the Estimated Answer Type (EAT) for a given query.
'''

DATE = ['WHEN', 'WHAT YEAR', 'IN WHAT YEAR', 'WHAT DAY', 'IN WHAT DAY']
LOCATION = ['WHERE',
            'WHAT CITY', 'IN WHAT CITY', 'IN WHICH CITY',
            'WHAT COUNTRY', 'IN WHAT COUNTRY', 'IN WHICH COUNTRY',
            'WHAT TOWN', 'IN WHAT TOWN', 'IN WHICH TOWN',
            'WHAT CONTINENT', 'IN WHAT CONTINENT', 'IN WHICH CONTINENT',
            'WHAT PLANET', 'IN WHAT PLANET', 'IN WHICH PLANET',
            'WHAT REGION', 'IN WHAT REGION', 'IN WHICH REGION',
            'WHAT AREA', 'IN WHAT AREA', 'IN WHICH AREA']
PERSON = ['WHO', 'WHOM', 'WHAT IS THE NAME OF', 'WHAT PERSON', 'WHAT MAN', 'WHAT WOMAN', 'WHAT COMPANY', 'WHAT ENTERPRISE']


def get_EAT(query):
    '''Return the Estimated Answer Type (EAT) of the query as a string'''

    query = query.upper()
    if any([item in query for item in DATE]): return 'DATE'
    if any([item in query for item in LOCATION]): return 'LOCATION'
    if any([item in query for item in PERSON]): return 'PERSON'