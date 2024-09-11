# FastAPI Project with Async SQLAlchemy, Prometheus & Grafana Monitoring

This project is a FastAPI application that includes PostgreSQL as the database and integrates Prometheus for monitoring and Grafana for visualizing metrics. The application uses SQLAlchemy 1.4+ with async functionality for efficient database interactions. It also includes rate-limiting, JWT-based authentication, and a full suite of unit tests.

## Features

- **FastAPI**: A modern web framework for building APIs with Python.
- **PostgreSQL**: A powerful, open-source relational database, used with async drivers.
- **Prometheus**: An open-source monitoring system to collect metrics and set alerts.
- **Grafana**: A tool to visualize data and metrics with powerful dashboards.
- **SQLAlchemy**: Async integration with PostgreSQL using SQLAlchemy 1.4+.
- **JWT Authentication**: Secure authentication with token expiration and refresh functionality.
- **Rate Limiting**: Protects the API from abuse by limiting the rate of requests.
- **Async**: Fully asynchronous endpoints and database interactions.
- **Docker**: Containerization of the entire environment for ease of development and deployment.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/nickshalnev/FastAPI-Async-SQLAlchemy-Prometheus-Grafana.git
cd FastAPI-Async-SQLAlchemy-Prometheus-Grafana
```

### 2. Add Environment Variables

Update the environment variables in `docker-compose.yml` or `.env` file:

- `DATABASE_URL`: Connection URL for PostgreSQL using asyncpg.
- `SECRET_KEY`: Secret key for JWT and other sensitive operations.

```env
DATABASE_URL=postgresql+asyncpg://postgres:mysecretpassword@db:5432/postgres
SECRET_KEY=pink-kittens
```

### 3. Docker Setup

This project uses Docker Compose to manage the application, database, Prometheus, and Grafana services.

To build and run the project:

```bash
docker-compose up --build
```

### 4. Accessing the Services

- **FastAPI Application**: [http://localhost:8000](http://localhost:8000)
- **Prometheus Monitoring**: [http://localhost:9090](http://localhost:9090)
- **Grafana Dashboards**: [http://localhost:3000](http://localhost:3000)

#### Grafana Login:

- **Username**: `admin`
- **Password**: `admin`

After logging in, you can set up Prometheus as a data source.

### 5. API Routes

The application provides several RESTful API routes for managing messages and user authentication. Here's an overview of the available routes:

#### **Messages API**

- **POST /messages/** - Create a new message.
  - **Request**: 
    ```json
    {
      "text": "Hello World!"
    }
    ```
  - **Response**:
    ```json
    {
      "id": 1,
      "text": "Hello World!"
    }
    ```

- **GET /messages/** - Retrieve all messages.
  - **Query Params**: `skip` (default: 0), `limit` (default: 10).
  - **Response**:
    ```json
    [
      {
        "id": 1,
        "text": "Hello World!"
      },
      {
        "id": 2,
        "text": "Another message"
      }
    ]
    ```

- **GET /messages/{message_id}** - Retrieve a message by ID.
  - **Response**:
    ```json
    {
      "id": 1,
      "text": "Hello World!"
    }
    ```

- **PUT /messages/{message_id}** - Update a message by ID.
  - **Request**:
    ```json
    {
      "text": "Updated message"
    }
    ```

  - **Response**:
    ```json
    {
      "id": 1,
      "text": "Updated message"
    }
    ```

- **DELETE /messages/{message_id}** - Delete a message by ID.
  - **Response**:
    ```json
    {
      "id": 1,
      "text": "Hello World!"
    }
    ```

#### **Auth API**

- **POST /auth/create-user** - Create a new user.
  - **Request**:
    ```json
    {
      "email": "user@example.com",
      "name": "John Doe",
      "password": "password123"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```

- **POST /auth/login** - User login.
  - **Request**:
    ```json
    {
      "email": "user@example.com",
      "password": "password123"
    }
    ```
  - **Response**:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```

- **GET /auth/refresh** - Refresh the user's authentication token.
  - **Response**:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```

### 6. Prometheus Configuration

Prometheus collects metrics from the FastAPI application and exposes them on the `/metrics` endpoint.

Configuration for Prometheus is in the `prometheus.yml` file. It scrapes metrics from the FastAPI application running at `web:8000`.

**prometheus.yml**:

```yaml
global:
  scrape_interval: 15s  # Interval at which metrics are scraped

scrape_configs:
  - job_name: 'fastapi_app'
    static_configs:
      - targets: ['web:8000']  # The FastAPI app container
```

### 7. Grafana Setup

Grafana is configured to run on port `3000`. Once Grafana is up and running:

1. Go to **Configuration** -> **Data Sources**.
2. Add **Prometheus** as a data source with the URL: `http://prometheus:9090`.
3. You can now create dashboards and visualize metrics from your FastAPI application.

### 8. API Rate Limiting

This project includes rate limiting using the **slowapi** package to protect the API from excessive requests.

- **Message Endpoints**: Limits to `30` requests per minute.
- **Auth Endpoints**: Limits are more stringent for critical operations, e.g., user login.

### 9. Running Tests

Unit tests are written using `pytest`, `pytest-asyncio`, and `AsyncMock`. They include full coverage of service files code.

To run the tests, execute:

```bash
pytest
```

### 10. Metrics and Monitoring

The application exposes important metrics, such as the number of requests, via the `/metrics` endpoint. These metrics are collected by Prometheus and visualized in Grafana.

Key Metrics:
- **Request Count**: Total number of requests handled by the FastAPI application.
- **Request Duration**: Time taken to process each request.
- **Database Queries**: Number of queries sent to the PostgreSQL database.

### 11. Volumes

This project uses Docker volumes to persist data between container restarts:

- **PostgreSQL Data**: Stored in `/var/lib/postgresql/data`.
- **Grafana Data**: Stored in `/var/lib/grafana`.

### 12. Troubleshooting

- **Grafana can't connect to Prometheus**: Ensure that the correct URL (`http://prometheus:9090`) is set in Grafana.
- **Prometheus is not scraping metrics**: Check the configuration in `prometheus.yml` and ensure the FastAPI app is running at `http://web:8000`.

## Conclusion

This project demonstrates the integration of modern tools like Prometheus, Grafana, and SQLAlchemy to create a robust, scalable API monitoring solution. By using Docker Compose, you can quickly spin up the entire environment and begin monitoring your services in real-time.

Feel free to fork, modify, and extend this setup for your own needs!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
