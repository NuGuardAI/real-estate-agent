# Real-Estate AI Agent Demo

Streamlit demo for a multi-agent real-estate assistant that searches listings, summarizes market context, and produces concise valuation notes.

## What’s included

- **Streamlit app UI** for collecting user criteria and showing results.
- **Direct Firecrawl extraction** to collect listing data from selected websites.
- **LLM agents** to produce market analysis and property valuation summaries.

## Architecture / design

**1) UI layer (Streamlit)**
- `app.py` renders the form, validates input, and orchestrates the analysis workflow.
- On submit, it calls `run_sequential_analysis()` and renders results via `display_properties_professionally()`.

**2) Data extraction layer**
- `DirectFirecrawlAgent` uses Firecrawl to extract listing data into a Pydantic schema (`PropertyListing` / `PropertyDetails`).
- URLs are constructed per selected site (Zillow, Realtor.com, Trulia, Homes.com).

**3) LLM agent workflow (sequential)**
- Uses the **agno** framework to build and run agents.
- `create_sequential_agents()` builds three roles:
	- Property Search Agent (parses Firecrawl results)
	- Market Analysis Agent (brief market insights)
	- Property Valuation Agent (concise per‑property assessment)
- `run_sequential_analysis()` coordinates the steps and returns structured data used by the UI.

**4) API layer (FastAPI)**
- `api.py` exposes `GET /health` and `POST /analyze`, wrapping the same `run_sequential_analysis()` pipeline for programmatic use.

## Setup

### Prerequisites

- Python 3.10+ recommended
- Firecrawl API key
- OpenAI API key

### Create and activate a virtual environment

```bash
python -m venv .venv
```

```powershell
.\.venv\Scripts\Activate.ps1
```

```cmd
.\.venv\Scripts\activate.bat
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

You can set the following environment variables in the shell or in a local .env file (recommended). A starter .env file is included.

- `FIRECRAWL_API_KEY`
- `OPENAI_API_KEY`
- `PORT` (optional, REST API only)

Example .env:

```dotenv
FIRECRAWL_API_KEY=your_firecrawl_key
OPENAI_API_KEY=your_openai_key
PORT=8251
```

Example (PowerShell):

```powershell
$env:FIRECRAWL_API_KEY="your_firecrawl_key"
$env:OPENAI_API_KEY="your_openai_key"
```

## Run

```bash
streamlit run app.py
```

## REST API

This project also exposes a REST API via FastAPI.

### Start the API

```bash
python api.py
```

If you prefer uvicorn directly, set the `PORT` in your shell and pass it through.

Note: To keep the server running in the foreground, start it in a normal terminal session (do not launch it as a detached/background process).

### Endpoints

- `GET /health` → health check
- `POST /analyze` → run the full analysis

### Request shape (POST /analyze)

Fields:
- `city` (string, required)
- `state` (string, optional)
- `min_price` (int, optional)
- `max_price` (int, optional)
- `property_type` (string, optional)
- `bedrooms` (string, optional)
- `bathrooms` (string, optional)
- `min_sqft` (int, optional)
- `special_features` (string, optional)
- `selected_websites` (array of strings, required)

```json
{
	"city": "San Francisco",
	"state": "CA",
	"min_price": 500000,
	"max_price": 1500000,
	"property_type": "Any",
	"bedrooms": "Any",
	"bathrooms": "Any",
	"min_sqft": 1000,
	"special_features": "Parking, Yard",
	"selected_websites": ["Zillow", "Realtor.com"]
}
```

### Response shape (POST /analyze)

Fields:
- `properties` (array of objects)
- `market_analysis` (string)
- `property_valuations` (string)
- `total_properties` (int)

```json
{
	"properties": [
		{
			"address": "...",
			"price": "...",
			"bedrooms": "...",
			"bathrooms": "...",
			"square_feet": "...",
			"property_type": "...",
			"description": "...",
			"features": ["..."],
			"images": ["..."],
			"agent_contact": "...",
			"listing_url": "..."
		}
	],
	"market_analysis": "...",
	"property_valuations": "...",
	"total_properties": 2
}
```

## Notes

- The UI allows selecting multiple listing sources and will return any listings extracted.
- Market analysis and valuation outputs are intentionally concise for display clarity.