import datetime
import uuid

from auth import Header
from typing import List
from rover_optimizer_sdk.models import Portfolio, Position
from rover_optimizer_sdk.models import WhitelistItem
from enum import Enum

class PortfolioStatus(Enum): 

    READY = "READY"
    PENDING = "PENDING"
    TERMINATED = "TERMINATED"

def create_cash_position(amount: int, port_id: str = None) -> Position: 
    """Creates a pure cash position as a Position object

    Args:
        amount (int): Amount to start the position with
        port_id (str, optional): Portfolio id for this position.If the value is None, it will give a random uuid to this position. Defaults to None.

    Returns:
        Position: Position object representing a position of just cash
    """
    assert amount > 0, "You need to have a positive cash amount in the position!"
    if port_id is None: 
        port_id = str(uuid.uuid1())

    cash_position = Position(
            id = 'USD', 
            asset_id='USD', 
            quantity=amount, 
            portfolio_id=port_id
        )

    return cash_position


def create_cash_portfolio(amount: int, port_id: None, created_at: str = None, 
currency: str = "USD", status: str = PortfolioStatus.READY, port_name: str = "Random") -> Portfolio: 
    """Creates a random cash portfolio with an amount you specify. 

    Args:
        amount (int): Amount to initialize the portfolio with
        port_id (str, optional): Portfolio identifier. Defaults to "Random".
        currency (str, optional): Currency of the portfolio. Defaults to "USD".
        status (str, optional): Portfolio status ENUM. Defaults to PortfolioStatus.READY.
        port_name (str, optional): Portfolio name. Defaults to "Random".

    Returns:
        Portfolio: Portfolio object which has only one cash position
    """
    if port_id is None: 
        port_id = str(uuid.uuid1())

    if created_at is None: 
        created_at = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

    cash_position = create_cash_position(amount=amount, port_id=port_id)

    portfolio = Portfolio(
            id = port_id, 
            created_at=created_at, 
            currency=currency, 
            positions = [cash_position], 
            status = status.value, 
            name = port_name
        ) 

    return portfolio

def create_whitelist(asset_ids: List[str]) -> List[WhitelistItem]: 

    whitelist = [] 
    for asset_id in asset_ids: 

        whitelist_item = WhitelistItem(
            asset_id=asset_id
        )

        whitelist.append(whitelist_item)

    return whitelist

