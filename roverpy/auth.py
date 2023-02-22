import os
import json 

from typing import Tuple, List
from dotenv import load_dotenv
from dataclasses import dataclass
from authenticator.credentials import Credentials
from elasticsearch import Elasticsearch

from rover_universe_sdk.models.get_assets_by_external_id_request import GetAssetsByExternalIdRequest
from rover_universe_sdk.models.get_assets_by_external_id_response import GetAssetsByExternalIdResponse
from rover_universe_sdk.api import AssetsApi

from rover_universe_sdk.models.get_external_id_mappings_request import GetExternalIdMappingsRequest
from rover_universe_sdk.models.get_external_id_mappings_response import GetExternalIdMappingsResponse
from rover_universe_sdk.api.external_id_mappings_api import ExternalIdMappingsApi

@dataclass
class Header: 
    """Header object which represents your authorization

    To enter into a request using python, make sure to use the to_dict() method

    Returns:
        Header: 
    """

    Authorization: str

    def to_dict(self): 

        head = {
            'Content-Type': 'application/json', 
            'Authorization': self.Authorization
        }

        return head

@dataclass 
class ElasticSearchCredentials: 

    cloudid: str
    username: str 
    password: str

def create_headers(yieldx_credentials: dict) -> Header: 
    """Creates the header to attach to your request through API

    Args:
        yieldx_credentials (dict): YieldX credentials as a dictionary. Usually comes from a json file you have

    Returns:
        dict: Dictionary representing the 
    """
    auth = "Bearer " + yieldx_credentials['access_token']
    header = Header(
        Authorization=auth
    )

    return header

def load_elastic_search_credentials(dotenv_path: str) -> ElasticSearchCredentials: 

    load_dotenv(dotenv_path = dotenv_path)

    cloudid = os.environ['ELASTIC_SEARCH_CLOUD_ID']
    username = os.environ['ELASTIC_USERNAME']
    password = os.environ['ELASTIC_PASSWORD']

    es_credentials = ElasticSearchCredentials(
    cloudid=cloudid, 
    username=username, 
    password=password
    )

    return es_credentials

def load_yieldx_credentials(dotenv_path: str) -> Credentials: 
    load_dotenv(dotenv_path=dotenv_path)

    yieldx_credentials_path = os.environ['YIELDX_CREDENTIALS_PATH']

    # Then we are going to create your yieldx credentials
    with open(yieldx_credentials_path, 'r') as f: 
        cred = json.load(f)


    credentials = Credentials(
        access_token=cred['access_token'], 
        token_type=cred['token_type'], 
        expires_in=cred['expires_in'], 
        scope=cred['scope']
    )

    return credentials

def load_headers(dotenv_path: str) -> Header: 
    yx = load_yieldx_credentials(dotenv_path=dotenv_path)

    headers = create_headers(yieldx_credentials=yx)

    return headers


def load_credentials(dotenv_path: str) -> Tuple[ElasticSearchCredentials, Credentials, Header]: 
    es_credentials = load_elastic_search_credentials(dotenv_path=dotenv_path)
    yx_credentials = load_yieldx_credentials(dotenv_path=dotenv_path)
    headers = load_headers(dotenv_path=dotenv_path)

    return es_credentials, yx_credentials, headers

def create_es(dotenv_path: str) -> Elasticsearch: 
    """Creates an Elasticsearch object using information in a json file

    Args:
        settings_json_path (str, optional): _description_. Defaults to 'settings.json'.

    Returns:
        Elasticsearch: Elasticsearch object to run searches through
    """

    es_credentials = load_elastic_search_credentials(dotenv_path=dotenv_path)

    es = Elasticsearch(
        cloud_id=es_credentials.cloudid, 
        basic_auth = (es_credentials.username, es_credentials.password)
    )

    return es


def get_assets_from_cusips(cusips: List[str], api: AssetsApi) -> GetAssetsByExternalIdResponse: 
    """Retrieves the assets objects from a list of cusips

    Args:
        cusips (List[str]): list of cusips you would like to get the assets for
        api (AssetsApi): api object to make the requests

    Returns:
        GetAssetsByExternalIdResponse: _description_
    """
    assert isinstance(api, AssetsApi), "You must specify an AssetsApi object"
    request = GetAssetsByExternalIdRequest(
        external_ids=cusips
    )
    try: 
        response = api.get_assets_by_external_id(source_name='cusip', get_assets_by_external_id_request = request)
        return response
    except Exception as e: 
        print(e)

def get_cusip_assed_id_mappings(cusips: List[str], api: ExternalIdMappingsApi) -> GetExternalIdMappingsResponse: 
    """Gets the cusip to asset id mappings for a list of cusips

    Args:
        cusips (List[str]): 
        api (ExternalIdMappingsApi): _description_

    Returns:
        GetExternalIdMappingsResponse: _description_
    """
    assert isinstance(api, ExternalIdMappingsApi), "You must specify an ExternalIdMappingsApi object"
    request = GetExternalIdMappingsRequest(
        external_ids=cusips
    )

    try: 
        response = api.get_external_id_mappings(source_name='cusip', get_external_id_mappings_request = request)
        return response
    except Exception as e: 
        print(e)




    







