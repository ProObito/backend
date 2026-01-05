
from .asura_scraper import AsuraScraper
from .comix_scraper import ComixScraper
from .roliascan_scraper import RoliaScanScraper
from .vortexscans_scraper import VortexScansScraper
from .reaperscans_scraper import ReaperScansScraper
from .stonescape_scraper import StoneScapeScraper
from .omegascans_scraper import OmegaScansScraper
from .allmanga_scraper import AllMangaScraper

SCRAPERS = {
    'asura': AsuraScraper,
    'comix': ComixScraper,
    'roliascan': RoliaScanScraper,
    'vortexscans': VortexScansScraper,
    'reaperscans': ReaperScansScraper,
    'stonescape': StoneScapeScraper,
    'omegascans': OmegaScansScraper,
    'allmanga': AllMangaScraper
}

__all__ = ['SCRAPERS'] + list(SCRAPERS.keys())
