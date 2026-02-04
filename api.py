from __future__ import annotations

import os
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agent import run_sequential_analysis

load_dotenv(override=True)

app = FastAPI(title="Real-Estate Agent API", version="1.0.0")

DEFAULT_FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_PORT = int(os.getenv("PORT", "8251"))


class PropertyRequest(BaseModel):
    city: str = Field(..., description="City to search")
    state: Optional[str] = Field(None, description="State/Province")
    min_price: Optional[int] = Field(0, description="Minimum price")
    max_price: Optional[int] = Field(0, description="Maximum price")
    property_type: Optional[str] = Field("Any", description="Property type")
    bedrooms: Optional[str] = Field("Any", description="Bedrooms")
    bathrooms: Optional[str] = Field("Any", description="Bathrooms")
    min_sqft: Optional[int] = Field(0, description="Minimum square feet")
    special_features: Optional[str] = Field("", description="Special features")
    selected_websites: List[str] = Field(..., description="Listing sources")


class PropertyResponse(BaseModel):
    properties: List[Dict[str, Any]]
    market_analysis: str
    property_valuations: str
    total_properties: int


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=PropertyResponse)
def analyze(req: PropertyRequest) -> PropertyResponse:
    if not req.selected_websites:
        raise HTTPException(status_code=400, detail="selected_websites must not be empty")

    if not DEFAULT_FIRECRAWL_API_KEY:
        raise HTTPException(status_code=500, detail="FIRECRAWL_API_KEY is not set")

    if not DEFAULT_OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    user_criteria = {
        "budget_range": f"${req.min_price:,} - ${req.max_price:,}",
        "property_type": req.property_type,
        "bedrooms": req.bedrooms,
        "bathrooms": req.bathrooms,
        "min_sqft": req.min_sqft,
        "special_features": req.special_features or "None specified",
    }

    def _noop_update(_progress: float, _status: str, _activity: Optional[str] = None) -> None:
        return None

    result = run_sequential_analysis(
        city=req.city,
        state=req.state or "",
        user_criteria=user_criteria,
        selected_websites=req.selected_websites,
        firecrawl_api_key=DEFAULT_FIRECRAWL_API_KEY,
        openai_api_key=DEFAULT_OPENAI_API_KEY,
        update_callback=_noop_update,
    )

    if isinstance(result, dict):
        return PropertyResponse(
            properties=result.get("properties", []),
            market_analysis=result.get("market_analysis", ""),
            property_valuations=result.get("property_valuations", ""),
            total_properties=result.get("total_properties", 0),
        )

    raise HTTPException(status_code=500, detail=str(result))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=DEFAULT_PORT)
