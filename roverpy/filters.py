from rover_optimizer_sdk.models import TextFilter, Filters

non_usd_text_filter = Filters(text = [TextFilter(
    key = 'id', 
    operator = 'Does not equal', 
    value = 'USD'
)])

usd_text_filter = Filters(text = [TextFilter(
    key = 'id', 
    operator = 'Equals', 
    value = 'USD'
)])

def create_asset_id_text_filter(asset_id: str) -> TextFilter: 

    return TextFilter(
        key = 'id', 
        operator='Equals', 
        value = asset_id
    )

