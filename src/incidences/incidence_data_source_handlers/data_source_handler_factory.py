incidences/incidence_data_source_handlers/data_source_handler_factory.py
import logging
from .zip_data_handler import ZipDataHandler
from .uncompressed_data_handler import UncompressedDataHandler

class DataSourceHandlerFactory:
    """
    Factory class to create the appropriate DataSourceHandler instance based on the data format.
    """

    @staticmethod
    def create_data_source_handler(source_config, base_data_dir=None, force_download=False):
        """
        Create and return the appropriate DataSourceHandler based on the source configuration.

        Parameters:
            source_config (dict): Configuration for the data source, including format and other settings.
            base_data_dir (str, optional): Base directory where data should be stored.
            force_download (bool, optional): If True, forces redownload of data.

        Returns:
            DataSourceHandler: An instance of either ZipDataHandler or UncompressedDataHandler.

        Raises:
            ValueError: If the specified data format is unsupported.
        """
        data_format = source_config.get("format", "uncompressed").lower()

        if data_format == "zip":
            logging.debug("Creating ZipDataHandler instance.")
            return ZipDataHandler(source_config, base_data_dir=base_data_dir, force_download=force_download)
        elif data_format == "uncompressed":
            logging.debug("Creating UncompressedDataHandler instance.")
            return UncompressedDataHandler(source_config, base_data_dir=base_data_dir, force_download=force_download)
        else:
            raise ValueError(f"Unsupported data format: {data_format}")