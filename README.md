### rover-py

This is a package which has a lot of useful rover python sdk functions and objects which may be useful for your general development. To use this package there are a couple of things you need
1. Rover python sdk packages installed 
2. `.env` file set up in your local repository

#### Setting up `.env` file

The basic information that you should store in your .env file are the following
```
ELASTIC_SEARCH_CLOUD_ID=rover-universe:......
ELASTIC_USERNAME={your elasticsearch username}
ELASTIC_PASSWORD={your elasticsearch password}
YIELDX_CREDENTIALS_PATH={path to yieldx credentials.json}
```

In many of the objects, you need to specify this path to your .env file and it will load up all the authentication from there

#### Examples

You can check out all relevant examples in the `examples` folder which will have notebooks showing you simple use cases

##### Quick example
```python 
from roverpy.auth import create_es 
from roverpy.optimization import BasicOptimization 
from roverpy.utils import portfolio_to_dataframe

# Importing APIs through rover
from rover_universe_sdk.api.assets_api import AssetsApi
from rover_portfolio_analyzer_sdk.api import PortfolioAnalyzerApi
from rover_optimizer_sdk.api import OptimizerApi

dotenv_path = {insert path to .env file here}

es = create_es(dotenv_path=dotenv_path)
opt_api = OptimizerApi()
analyzer_api = PortfolioAnalyzerApi() 
assets_api = AssetsApi()

query = {}

optimization = BasicOptimization(
    dotenv_path=dotenv_path, 
    optimizer_api=opt_api, 
    assets_api = assets_api, 
    analyzer_api = analyzer_api
)

portfolio = optimization.run_optimization_on_search(
    query = query
)

```
