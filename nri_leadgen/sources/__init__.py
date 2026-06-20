from .seed_csv import SeedCSVSource
from .sec_edgar import SECEdgarSource
from .ipo_ma import IPOMASource
from .crunchbase import CrunchbaseSource
from .web_search import WebSearchSource
from .apollo import ApolloSource

REGISTRY = {
    "seed_csv": SeedCSVSource,
    "sec_edgar": SECEdgarSource,
    "ipo_ma": IPOMASource,
    "crunchbase": CrunchbaseSource,
    "web_search": WebSearchSource,
    "apollo": ApolloSource,
}
