import pandas as pd 
import requests

from rover_optimizer_sdk.models import (
    WhitelistItem, 
    Portfolio, 
    Position
)
from rover_universe_sdk.models import Asset, Bond
from rover_universe_sdk.api import AssetsApi
from rover_universe_sdk.models.get_asset_response import GetAssetResponse
from rover_universe_sdk.models.get_assets_request import GetAssetsRequest

from rover_portfolio_analyzer_sdk.api import PortfolioAnalyzerApi
from rover_portfolio_analyzer_sdk.models.analyze_portfolio_request import AnalyzePortfolioRequest
from rover_portfolio_analyzer_sdk.models.analyze_portfolio_response import AnalyzePortfolioResponse

from roverpy.utils import portfolio_to_dataframe

from elastic_transport import ObjectApiResponse
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

def create_summary_df(portfolio: Portfolio, asset_api: AssetsApi, analyzer_api: PortfolioAnalyzerApi) -> pd.DataFrame: 
    """Creates a summary dataframe from a portfolio response object

    Args:
        portfolio (Portfolio): Target portfolio to turn into a dataframe

    Returns:
        pd.DataFrame: Dataframe which shows useful information for these set of positions
    """

    def extract_asset_information(asset: Asset) -> dict: 
        info = {} 

        info['asset_id'] = asset.id
        info['cusip'] = asset.identifiers.cusip 
        info['description'] = asset.description
        info['yield'] = asset.analytics._yield

        return info
    
    portfolio_df = portfolio_to_dataframe(portfolio=portfolio)

    # Preparing the get assets request so we can see basic information
    asset_ids = list(portfolio_df['asset_id'])
    asset_ids.remove("USD")

    get_assets_request = GetAssetsRequest(asset_ids=asset_ids)
    get_assets_response = asset_api.get_assets(get_assets_request = get_assets_request)

    asset_information = [extract_asset_information(asset) for asset in get_assets_response.assets]
    df = pd.DataFrame.from_records(asset_information)
    merged_df = portfolio_df.merge(right = df, how = 'left', on = 'asset_id')

    # Then we get the weight information from the api using the analyzer service
    analyze_request = AnalyzePortfolioRequest(
    portfolio=portfolio
    )

    analyze_response = analyzer_api.analyze_portfolio(analyze_portfolio_request = analyze_request)

    weights = analyze_response.analysis.weights
    weights_df = pd.DataFrame.from_records([w.to_dict() for w in weights])

    final_summary_df = merged_df.merge(weights_df, how = 'left', left_on = 'id', right_on = 'position_id')
    cols = ['asset_id', 'cusip', 'description', 'quantity', 'yield', 'weight']
    return final_summary_df[cols]
