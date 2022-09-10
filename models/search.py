from contextlib import suppress
from dataclasses import dataclass
from json import JSONDecodeError
from turtle import title
from typing_extensions import dataclass_transform
from pydantic import BaseModel
from typing import Optional
import requests
from requests import get


@dataclass
class Dimension:
    width: Optional[int]
    height: Optional[int]


@dataclass
class Text:
    title: str
    shortTitle: str
    caption: str
    seo_title: str
    seo_caption: str
    description: str  # altText


class ImageRequest(BaseModel):
    query: str
    page: int
    language: Optional[str] = "en"


@dataclass
class SearchMetadata:
    title: str
    description: Optional[str]
    canonical_url: Optional[str]
    hero_image: Optional[str]


class Image(BaseModel):
    image_id: str
    assetType: Optional[str]
    istockCollection: Optional[str]
    thumbUrl: Optional[str]
    release_code: Optional[str]
    mediaType: Optional[str]
    dateSubmitted: Optional[str]
    slot: Optional[int]
    orientation: Optional[str]
    usageInfo: Optional[str]
    uploadDate: Optional[str]
    maxDimensions: Optional[Dimension]
    text: Optional[Text]


class Search(BaseModel):
    results: list[Image]
    total_number_of_results: Optional[int]
    related_terms: list[Optional[str]]
    search_metadata: Optional[SearchMetadata]

    def get_search_images(self, reqt: ImageRequest):
        url = f"https://www.istockphoto.com/{reqt.language}/search/2/image?phrase={reqt.query}&page={reqt.page}"

        headers = {
            "authority": "www.istockphoto.com",
            "accept": "application/json",
            "accept-language": "fr-FR,fr-MA;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6",
            "sec-ch-ua": '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
        }
        for _ in range(3):
            try:
                response = get(url, headers=headers, timeout=3)
                if response.status_code == 200:
                    with suppress(JSONDecodeError):
                        self._parse_data(response.json())
                        return self
            except requests.exceptions.RequestException:
                continue
        raise Exception("Error while fetching data")

    def _parse_data(self, data: dict):
        assets = data.get("gallery", {}).get("assets", [])
        self.results = [
            Image(
                image_id=asset.get("id"),
                assetType=asset.get("assetType"),
                istockCollection=asset.get("istockCollection"),
                thumbUrl=asset.get("thumbUrl"),
                release_code=asset.get("releaseCode"),
                mediaType=asset.get("mediaType"),
                dateSubmitted=asset.get("dateSubmitted"),
                slot=asset.get("slot"),
                orientation=asset.get("orientation"),
                usageInfo=asset.get("usageInfo"),
                uploadDate=asset.get("uploadDate"),
                maxDimensions=Dimension(
                    width=asset.get("maxDimensions", {}).get("width"),
                    height=asset.get("maxDimensions", {}).get("height"),
                ),
                text=Text(
                    title=asset.get("text", {}).get("title"),
                    shortTitle=asset.get("text", {}).get("shortTitle"),
                    caption=asset.get("text", {}).get("caption"),
                    seo_title=asset.get("text", {}).get("seoTitle"),
                    seo_caption=asset.get("text", {}).get("seoCaption"),
                    description=asset.get("text", {}).get("altText"),
                ),
            )
            for asset in assets
        ]
        self.total_number_of_results = data["total_number_of_results"]
        self.related_terms = data["related_terms"]
        self.search_metadata = SearchMetadata(**data.get("pageMetaData", {}))
