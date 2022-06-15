import requests
from requests.auth import HTTPBasicAuth


def search(search_term):
    auth = HTTPBasicAuth("USERNAME", "PASSWORD")
    with requests.Session() as session:
      params = {'q':search_term, 'content': 'SCIENTIFIC_NAME', 'maxRank':'SPECIES', 'type': 'EXACT', 'offset':0, 'limit':10}
  
      try:
        r = requests.get('https://api.catalogueoflife.org/dataset/3LR/nameusage/search', params=params, headers={'accept': 'application/json'})
      except requests.exceptions.RequestException:
        return ['Error retrieving taxon: %s' % search_term]
      else: 
        rdata = r.json()
        if rdata['empty']:
          return False
    return rdata['result']

def getSynonyms(search_term):
    auth = HTTPBasicAuth("USERNAME", "PASSWORD")
    with requests.Session() as session:
      params = {'q':search_term, 'content': 'SCIENTIFIC_NAME', 'maxRank':'SPECIES', 'type': 'EXACT', 'offset':0, 'limit':10}
  
      try:
        r = requests.get('https://api.catalogueoflife.org/dataset/3LR/nameusage/search', params=params, headers={'accept': 'application/json'})
      except requests.exceptions.RequestException:
        return [None, 'Error retrieving taxon: %s' % search_term]
      else:
        rdata = r.json()
        if rdata['empty']:
          return ['No match for %s found.' % search_term]
  
        closest = rdata['result'][0]
        taxonID = closest['id']
        datasetKey = closest['usage']['datasetKey']
  
        try:
          r = requests.get('https://api.catalogueoflife.org/dataset/%s/taxon/%s/synonyms' % (datasetKey, taxonID), auth=auth, headers={"Content-Type": "application/json"})
        except requests.exceptions.RequestException:
          return [None, 'Unable to retrieve synonyms for %s.' % search_term]
        else:
          synonyms = []
          rdata = r.json()
          if not rdata:
            return ['No synonyms available for %s.' % search_term]
          for synonym_type in rdata:
            for synonym in rdata[synonym_type]:
                synonyms.append(synonym[0]['scientificName'])
  
          synonyms.sort()
          return synonyms
