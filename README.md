# User Service

This microservice provides a simple API for user.

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/SoloAWS/user-service.git
   cd user-service
   ```

2. Create and activate a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Running the Service

To run the service locally:

```
uvicorn main:app --reload --port 8002
```

The service will be available at `http://localhost:8002`.

## API Endpoints

- `GET /user/health`: Health check endpoint

## Docker

To build and run the Docker container:

```
docker build -t user-service .
docker run -p 8002:8002 user-service
```

Make sure to expose port 8002 in your Dockerfile:

```dockerfile
EXPOSE 8002
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```
