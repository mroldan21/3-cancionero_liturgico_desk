"""Paquete core: lógica de negocio."""

from .database import database
from .file_processor import file_processor
from .ocr_engine import ocr_engine
from .web_scraper import web_scraper

__all__ = ["database", "file_processor", "ocr_engine", "web_scraper"]