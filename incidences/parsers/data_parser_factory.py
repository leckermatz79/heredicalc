# V3/incidences/parsers/data_parser_factory.py
import logging
from V3.incidences.parsers.ci5_detailed_parser import CI5DetailedParser
from V3.incidences.parsers.ci5_summary_parser import CI5SummaryParser
from V3.incidences.parsers.data_parser import DataParser

class DataParserFactory:
    """Factory for creating data parsers based on dataset type."""

    @staticmethod
    def create_parser(source_config, population=None):
        parser_type = source_config.get("parser")
        
        if parser_type == "ci5_detailed_parser":
            return CI5DetailedParser(source_config, population)
        elif parser_type == "ci5_summary_parser":
            return CI5SummaryParser(source_config, population)
        else:
            logging.error(f"Unknown parser type: {parser_type}")
            raise ValueError(f"Unsupported parser type: {parser_type}")