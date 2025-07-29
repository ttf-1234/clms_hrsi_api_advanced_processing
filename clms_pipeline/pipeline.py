from clms_pipeline.steps.downloader import Downloader
from clms_pipeline.steps.tile_determiner import TileDeterminer
from clms_pipeline.steps.mosaic import MosaicBuilder
from clms_pipeline.steps.reclassify import Reclassifier
from clms_pipeline.steps.resample import Resampler
from clms_pipeline.steps.cloud_filter import CloudFilter
from clms_pipeline.steps.unzipper import Unzipper

class CLMSPipeline:
    def __init__(self, config):
        self.config = config
        self.downloader = Downloader(config)
        self.tile_determiner = TileDeterminer(config)
        self.mosaic_builder = MosaicBuilder(config)
        self.reclassifier = Reclassifier(config)
        self.resampler = Resampler(config)
        self.cloud_filter = CloudFilter(config)
        self.unzipper = Unzipper(config)

    def run(self):
        self.tile_determiner.determine_tiles()
        self.downloader.download()
        self.unzipper.unzip_and_cleanup()
        self.mosaic_builder.build_mosaic()
        self.reclassifier.reclassify()
        self.resampler.resample()
        self.cloud_filter.filter_clouds()
