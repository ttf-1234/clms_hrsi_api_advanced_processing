from config import config
from clms_pipeline.pipeline import CLMSPipeline

pipeline = CLMSPipeline(config)
pipeline.run()
