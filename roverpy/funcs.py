import pandas as pd 
import requests

from rover_universe_sdk.models import Asset, Bond
from typing import List 


def get_live_offers(cusips: List[str], headers: dict) -> pd.DataFrame: 
    """Takes a list of cusips and your headers file. Returns a pandas dataframe of all offers in the market

    Args:
        cusips (List[str]): List of cusips as strings
        headers (dict): Headers to put into the request

    Returns:
        pd.DataFrame: Dataframe of live offers for the set of cusips supplied
    """
    ice_data_url = 'https://dev.yieldx.app/apis/ice-data/v1/cusips'
    ice_data_response = requests.post(
        url = ice_data_url, 
        json = {'cusips': cusips}, 
        headers = headers
    )

    ice_data_dict = ice_data_response.json()
    ice_data = ice_data_dict['cusipIceMappings']

    entry_type = 'OFFER'
    def parse_offers(ice_data_list: list) -> list: 
        offers = []
        for ice in ice_data_list:
            if ice['entryType'] == entry_type: 
                offers.append(ice)

        return offers 

    offers = []

    # Going through every entry and taking out the offer information
    for ice_entry in ice_data: 
        d = ice_entry['iceData']
        off = parse_offers(ice_data_list = d)
        offers.extend(off)

    offers_df = pd.DataFrame(offers)

    return offers_df


def extract_asset_info(asset: Asset) -> dict: 
    info = {} 

    if asset.identifiers is not None: 
        info['asset_id'] = asset.id
        info['cusip'] = asset.identifiers.cusip
        info['isin'] = asset.identifiers.isin 
        info['description'] = asset.name 
        info['rating'] = asset.rating 
        info['yield'] = asset.analytics._yield
        info['duration'] = asset.analytics.duration 
        info['price'] = asset.price
        info['years_to_maturity'] = asset.analytics.years_to_maturity
        info['use_of_proceeds'] = asset.bond.use_of_proceeds
        info['debt_service_type'] = asset.bond.debt_service_type  
        info['sector'] = asset.bond.issuer.sector      

    return info