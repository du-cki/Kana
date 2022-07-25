from __future__ import annotations
from typing import TYPE_CHECKING

from starlette.convertors import Convertor
from starlette.convertors import register_url_convertor # type: ignore

if TYPE_CHECKING:
    from .app import App

class UUIDConvertor(Convertor["App"]):
    regex = "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    def convert(self, value: str) -> str: # type: ignore
        return value

register_url_convertor("UUID", UUIDConvertor())

def predict_media_type(fmt: str) -> str:
    if fmt in ["png", "jpg", "jpeg", "webp", "gif"]:
        return "image/" + fmt
    else:
        return "application/octet-stream"
