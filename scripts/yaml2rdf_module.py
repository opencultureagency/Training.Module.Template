'''
Converts ASKotec training module meta-data
(from module.yaml) into an RDF/Turtle.
'''

import glob
import os
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
import wget
from yaml2rdf_shared import *
from yaml2rdf import convert

KEY_RESOURCE_URL_YAML = 'yaml-url'
KEY_RESOURCE_URL_RDF = 'rdf-url'
KEY_RESOURCE_FILE_RDF = 'rdf-file'

def download(url, path):
    '''
    Downloads a URL pointing to a file into a local file,
    pointed to by path.
    '''
    print('downloading %s to %s ...' % (url, path))
    if os.path.exists(path):
        os.remove(path)
    wget.download(url, path, None)

def ensure_resource_turtles(yaml_cont, g):
    '''
    Either downloads the reosurce RDF files directly,
    or downloads their YAML version, an dconverts them to RDF afterwards.
    '''

    res_i = 0
    for elem in yaml_cont['resources']:
        if KEY_RESOURCE_URL_YAML in elem:
            res_yml_url = elem[KEY_RESOURCE_URL_YAML]
            res_yml_file = os.path.join(os.path.curdir,
                    'resource_%d.yml' % res_i)
            res_ttl_file = os.path.join(os.path.curdir,
                    'resource_%d.ttl' % res_i)
            res_pre_file = os.path.join(os.path.curdir,
                    'resource_%d.pref' % res_i)
            download(res_yml_url, res_yml_file)
            convert(res_yml_file, res_ttl_file, res_pre_file)
            yaml_cont[KEY_RESOURCE_FILE_RDF] = res_ttl_file
        elif KEY_RESOURCE_URL_RDF in elem:
            res_ttl_url = elem[KEY_RESOURCE_URL_RDF]
            res_ttl_file = os.path.join(os.path.curdir,
                    'resource_%d.ttl' % res_i)
            download(res_ttl_url, res_ttl_file)
            yaml_cont[KEY_RESOURCE_FILE_RDF] = res_ttl_file
        else:
            conv_fail('Resource needs either of %s or %s spezified'
                    % (KEY_RESOURCE_URL_YAML, KEY_RESOURCE_URL_RDF))
        res_i = res_i + 1


def convert_module_yaml_to_rdf(yaml_cont, g):
    '''
    Converts ASKotec training module meta-data content
    into an RDF/Turtle string.
    '''

    supported_version = "1.0"
    if version_compare(yaml_cont['version'], supported_version) < 0:
        raise 'The content version is not supported by this converter. Please get a newer version!'

    y = yaml_cont['module']
    pre_path = 'module'

    m_s = ASKM[str2id(y['name'])]

    ensure_resource_turtles(y, g)
    for res_ttl in glob.glob('resource_*.ttl'):
        g.parse(res_ttl, format='ttl')
    for res_s,_,_ in g.triples((None, RDF['type'], ASK['Resource'])):
        g.add(( m_s, ASK.resource, res_s ))

    g.add(( m_s, RDF.type, ASK.Module ))
    g.add(( m_s, RDFS.label, rdf_str(y['name']) ))
    if 'manual' in y:
        g.add(( m_s, ASK.manual, rdf_str(y['manual']) ))
    elif os.path.exists('manual.md'):
        g.add(( m_s, ASK.manual, rdf_str('manual.md') ))
    else:
        conv_fail('Entry not found "%s", and default path "%s" does not exist'
                % (pre_path + '.' + 'manual', os.path.curdir + '/manual.md'))
    g.add(( m_s, ASK.release, rdf_str(y['release']) ))
    g.add(( m_s, ASK.duration, rdf_str(y['duration']) ))
    g.add(( m_s, ASK.maxParticipians, rdf_str(y['max-participians']) ))
    g.add(( m_s, ASK.compatibility, rdf_str(y['compatibility']) ))
    g.add(( m_s, ASK.blogPosts, rdf_str(y['blog-posts']) ))
    g.add(( m_s, ASK.issues, rdf_str(y['issues']) ))
    g.add(( m_s, ASK.newIssue, rdf_str(y['new-issue']) ))

    conv_authors(y, g, m_s)
    conv_licenses(y, g, m_s)
