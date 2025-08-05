# DeliverHook

**DeliverHook** is a robust backend system that functions as a reliable webhook delivery service. This service ingests incoming webhooks, queues them, and attempts delivery to subscribed target URLs, handling failures with retries and providing visibility into the delivery status.


## 🚀 Features

- **Subscription Management:** CRUD operations for webhook subscriptions...
- **Webhook Ingestion:** Accepts incoming webhook payloads with signature verification  
- **Asynchronous Delivery:** Background workers process delivery tasks  
- **Retry Mechanism:** Exponential backoff with configurable max attempts  
- **Delivery Logging:** Comprehensive logging of delivery attempts  
- **Log Retention:** Automatic cleanup of old logs  
- **Status & Analytics:** Endpoints for monitoring delivery status  
- **Event Type Filtering:** Filter webhooks based on event types  
- **Payload Signature Verification:** Secure webhook delivery with HMAC-SHA256  

---

## 🏗 Architecture

### 🔧 Tech Stack

- **Framework:** FastAPI (Python)  
- **Database:** PostgreSQL  
- **Cache & Queue:** Redis  
- **Task Queue:** Celery  
- **Containerization:** Docker & Docker Compose  

### 🧩 Components

- **API Service:** Handles HTTP requests and manages subscriptions  
- **Worker Service:** Processes webhook deliveries asynchronously  
- **Database:** Stores subscriptions and delivery logs  
- **Redis:** Caches subscription data and serves as Celery broker  

---

## ⚙️ Setup Instructions

### ✅ Prerequisites

- Docker  
- Docker Compose  

### 🛠 Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/ArthSonani/DeliverHook.git
   cd deliverhook

