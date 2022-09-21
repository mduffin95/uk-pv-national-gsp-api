""" Main FastAPI app """
import logging
import os
import time
from datetime import timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from starlette.responses import HTMLResponse

from gsp import router as gsp_router
from national import router as national_router
from status import router as status_router
from system import router as system_router

logging.basicConfig(
    level=getattr(logging, os.getenv("LOGLEVEL", "DEBUG")),
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

title = "Nowcasting API"
version = "0.2.27"
description = """
As part of Open Climate Fix’s [open source project](https://github.com/openclimatefix), the
Nowcasting API is still under development.

#### General Overview

__Nowcasting__ essentially means __forecasting for the next few hours__.
OCF has built a predictive model that nowcasts solar energy generation for
the UK’s National Grid ESO (electricity system operator). National Grid runs more than
300
[GSPs](https://data.nationalgrideso.com/system/gis-boundaries-for-gb-grid-supply-points)
(grid supply points), which are regionally located throughout the country.
OCF's Nowcasting App synthesizes real-time PV
data, numeric weather predictions (nwp), satellite imagery
(looking at cloud cover),
as well as GSP data to
forecast how much solar energy will generated for a given GSP.

Here are key aspects of the solar forecasts:
- Forecasts are produced in 30-minute time steps, projecting GSP yields out to
eight hours ahead.
- The geographic extent is all of Great Britain (GB).
- Forecasts are produced at the GB National and regional level (using GSPs).

OCF's incredibly accurate, short-term forecasts allow National Grid to reduce the amount of
spinning reserves they need to run at any given moment, ultimately reducing
carbon emmisions.

In order to get started with reading the API’s forecast objects, it might be helpful to
know that GSPs are referenced in the following ways:  gspId (ex. 122); gspName
(ex. FIDF_1); gspGroup (ex. )
regionName (ex. Fiddlers Ferry). The API provides information on when input data was
last updated as well as the installed photovoltaic (PV) megawatt capacity
(installedCapacityMw) of each individual GSP.

You'll find more detailed information for each route in the documentation below.

If you have any questions, please don't hesitate to get in touch.
And if you're interested in contributing to our open source project, feel free to join us!
"""
app = FastAPI()

origins = os.getenv("ORIGINS", "https://app.nowcasting.io").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time into response object header"""
    start_time = time.time()
    response = await call_next(request)
    process_time = str(time.time() - start_time)
    logger.debug(f"Process Time {process_time}")
    response.headers["X-Process-Time"] = process_time
    return response


thirty_minutes = timedelta(minutes=30)


# Dependency
v0_route_solar = "/v0/solar/GB"
v0_route_system = "/v0/system/GB"

app.include_router(national_router, prefix=f"{v0_route_solar}/national")
app.include_router(gsp_router, prefix=f"{v0_route_solar}/gsp")
app.include_router(status_router, prefix=f"{v0_route_solar}")
app.include_router(system_router, prefix=f"{v0_route_system}/gsp")
# app.include_router(pv_router, prefix=f"{v0_route}/pv")


@app.get("/")
async def get_api_information():
    """### Get basic information about the Nowcasting API

    The object returned contains basic information about the Nowcasting API.

    """

    logger.info("Route / has be called")

    return {
        "title": "Nowcasting API",
        "version": version,
        "description": description,
        "documentation": "https://api.nowcasting.io/docs",
    }


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> FileResponse:
    """Get favicon"""
    return FileResponse("src/favicon.ico")

def get_redoc_html_with_theme(
    *,
    openapi_url: str = "./openapi.json",
    title: str,
    redoc_js_url: str = "https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    redoc_favicon_url: str = "/favicon.png",
    with_google_fonts: bool = True,
    theme = {}
) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>{title}</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    """
    if with_google_fonts:
        html += """
    <link href="https://fonts.googleapis.com/css?family=Inter:300,400,700" rel="stylesheet">
    """
    html += f"""
    <link rel="shortcut icon" href="{redoc_favicon_url}">
    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
    </head>
    <body>
    <div id="redoc-container"></div>
    <noscript>
        ReDoc requires Javascript to function. Please enable it to browse the documentation.
    </noscript>
    <script src="{redoc_js_url}"> </script>
    <script>
        Redoc.init("{openapi_url}", """ + """{
            "theme": {
                "colors": {
                    "primary": {
                        "main": "#f7ba17",
                        "light": "#ffefc6"
                    },
                    "success": {
                        "main": "rgba(28, 184, 65, 1)",
                        "light": "#81ec9a",
                        "dark": "#083312",
                        "contrastText": "#000"
                    },
                    "text": {
                        "primary": "#14120e",
                        "secondary": "#4d4d4d"
                    },
                    "http": {
                        "get": "#f7ba17",
                        "post": "rgba(28, 184, 65, 1)",
                        "put": "rgba(255, 187, 0, 1)",
                        "delete": "rgba(254, 39, 35, 1)"
                    }
                },
                "typography": {
                    "fontSize": "15px",
                    "fontFamily": "Inter, sans-serif",
                    "lineHeight": "1.5em",
                    "headings": {
                        "fontFamily": "Inter, sans-serif",
                        "fontWeight": "bold",
                        "lineHeight": "1.5em"
                    },
                    "code": {
                        "fontWeight": "600",
                        "color": "rgba(92, 62, 189, 1)",
                        "wrap": true
                    },
                    "links": {
                        "color": "#086788",
                        "visited": "#086788",
                        "hover": "#32343a"
                    }
                },
                "sidebar": {
                    "width": "300px",
                    "textColor": "#000000"
                },
                "logo": {
                    "gutter": "10px"
                },
                "rightPanel": {
                    "backgroundColor": "rgba(55, 53, 71, 1)",
                    "textColor": "#ffffff"
                }
            }
        }""" + f""", document.getElementById('redoc-container'))
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.get("/newdocs", include_in_schema=False)
async def redoc_html():
    """### Render ReDoc with custom theme options included"""
    return get_redoc_html_with_theme(
        title=title,
        theme={}
    ) 

# OpenAPI (ReDoc) custom theme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=title,
        version=version,
        description=description,
        contact={
            "name": "Open Climate Fix",
            "url": "https://openclimatefix.org",
            "email": "info@openclimatefix.org",
        },
        license_info={
            "name": "MIT License",
            "url": "https://github.com/openclimatefix/nowcasting_api/blob/main/LICENSE",
        },
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.nowcasting.io/nowcasting.svg"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi