from fastapi import APIRouter, Depends, HTTPException
from models.search import SearchRequest, Search

router = APIRouter(prefix="/istock/search", tags=["iStock"])


@router.get("/search")
def get_searched_images(query: str, page: int, language: str = "en"):
    try:
        reqt = SearchRequest(query=query, page=page, language=language)
        return Search().get_search_images(reqt)
    except ValueError as e:
        raise HTTPException(status_code=406, detail=str(e)) from e
