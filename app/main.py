from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import subscriptions, ingest, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Webhook Delivery Service",
    description="""
    A robust webhook delivery service that handles subscription management, 
    webhook ingestion, and asynchronous delivery with retries and logging.
    
    ## Features
    
    ### Subscription Management
    - Create, read, update, and delete webhook subscriptions
    - Configure target URLs and secret keys
    - Set up event type filtering
    
    ### Webhook Ingestion
    - Secure endpoint for receiving webhooks
    - HMAC-SHA256 signature verification
    - Event type validation
    - Asynchronous processing
    
    ### Delivery Processing
    - Background worker processing
    - Exponential backoff retry mechanism
    - Configurable retry attempts
    - Comprehensive delivery logging
    
    ### Status & Analytics
    - Real-time delivery status tracking
    - Detailed delivery attempt history
    - Subscription-specific analytics
    - Configurable log retention
    
    ## Security
    
    - All endpoints require authentication
    - Webhook signature verification
    - Event type filtering
    - Rate limiting
    
    ## Rate Limits
    
    - API endpoints: 100 requests per minute
    - Webhook ingestion: 1000 requests per minute
    
    ## Error Codes
    
    - 400: Bad Request
    - 401: Unauthorized
    - 403: Forbidden
    - 404: Not Found
    - 429: Too Many Requests
    - 500: Internal Server Error
    
    ## Support
    
    For support, please contact the developer.
    """,
    version="1.0.0",
    docs_url=None,
    redoc_url="/redoc",
    contact={
        "name": "Pal Zadafiya",
        "email": "zadafiya.pal@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "subscriptions",
            "description": "Operations with webhook subscriptions",
        },
        {
            "name": "ingest",
            "description": "Webhook ingestion and processing",
        },
        {
            "name": "status",
            "description": "Delivery status and analytics",
        },
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
app.include_router(status.router, prefix="/status", tags=["status"])

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Webhook Delivery Service API",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info,
        tags=app.openapi_tags,
    ) 