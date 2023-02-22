import pandas as pd

from typing import List
from elastic_transport import ObjectApiResponse
from rover_optimizer_sdk.api import OptimizerApi
from rover_optimizer_sdk.models import OptimizePortfolioRequest, OptimizePortfolioResponse
from rover_optimizer_sdk.models import (
    WhitelistItem, 
    InstrumentConcentrationConstraint, 
    MinimumTradeSizeConstraint, 
    Constraints, 
    Portfolio, 
    Position, 
    MaximizeYieldObjective, 
    Objectives
)

from rover_universe_sdk.api import AssetsApi
from rover_portfolio_analyzer_sdk.api import PortfolioAnalyzerApi

from roverpy.filters import non_usd_text_filter, usd_text_filter
from roverpy.auth import create_es
from roverpy.utils import create_cash_portfolio, create_whitelist_from_search
from roverpy.funcs import create_summary_df

class BasicOptimization: 

    def __init__(self, dotenv_path: str, optimizer_api: OptimizerApi, assets_api: AssetsApi, analyzer_api: PortfolioAnalyzerApi) -> None: 
        
        self.opt_api = optimizer_api
        self.assets_api = assets_api
        self.analyzer_api = analyzer_api
        self.es = create_es(dotenv_path = dotenv_path)
        self.elastic_search = None

    def run_search(self, query: dict, size: int = 1000, index: str = 'rover-universe-assets') -> ObjectApiResponse: 

        assert self.es, "Elasticsearch object has to be initialized!"

        search = self.es.search(
            index = index, 
            size = size, 
            query = query
        )

        return search
    
    def run_optimization_on_search(self, query: dict, max_instrument_concentration: float = 0.10, min_trade_size: float = 0.01, 
        size: int = 1000, index: str = 'rover-universe-assets', portfolio_starting_cash: int = 100_000) -> pd.DataFrame: 

        search = self.run_search(
            query = query, 
            index = index, 
            size = size
        )

        # Create the whitelist 
        whitelist = create_whitelist_from_search(elastic_search_response=search)

        # Create the portfolio of cash to start
        portfolio = create_cash_portfolio(amount = portfolio_starting_cash)

        # Creating basic constraints
        instrument_concentration = InstrumentConcentrationConstraint(
            filters=non_usd_text_filter, 
            maximum_weight=max_instrument_concentration
        )

        min_trade_size_constraint = MinimumTradeSizeConstraint(
            filters=non_usd_text_filter, 
            minimum_weight=min_trade_size
        )

        constraints = Constraints(
            instrument_concentration=[instrument_concentration], 
            minimum_trade_size=[min_trade_size_constraint]
        )

        # Then we set a maximize yield constraint here
        max_yield_obj = MaximizeYieldObjective(weight = 1)
        objectives = Objectives(
            maximize_yield=max_yield_obj
        )

        # Then we are going to create the request
        request = OptimizePortfolioRequest(
            portfolio=portfolio, 
            whitelist=whitelist, 
            objectives=objectives, 
            constraints=constraints
        )

        port = self.opt_api.optimize_portfolio(optimize_portfolio_request = request)

        # Once we get this portfolio, we can create the summary dataframe for it
        summary_df = create_summary_df(
            portfolio=port.portfolio, 
            asset_api=self.assets_api, 
            analyzer_api=self.analyzer_api
        )

        return summary_df
        

    