# MP3 Converter Microservices

This project is a microservice-based system for converting audio files to MP3, built with **FastAPI**, **RabbitMQ**, **PostgreSQL**, **MinIO**, and deployed on **Kubernetes**.  
I developed this to learn about microservice architecture and Kubernetes.

## Architecture

The system is composed of the following services:

-   **Auth Service**  
    Handles user registration, login, and JWT-based authentication. Stores users in PostgreSQL.

-   **Gateway Service**  
    Exposes a single entrypoint (via Ingress). Forwards requests to other services, validates tokens, and queues conversion jobs.

-   **Worker Service**  
    Consumes audio conversion jobs from RabbitMQ, downloads the file, converts it to MP3 using `ffmpeg`, uploads the result to MinIO, and publishes a notification event.

-   **Notification Service**  
    Listens for completed conversion events, generates secure download tokens via the Gateway, and sends email notifications using the Resend API.

-   **Postgres**  
    Stores user accounts for the Auth service.

-   **RabbitMQ**  
    Message broker for job and notification queues.

-   **MinIO**  
    S3-compatible object storage for converted MP3 files.

## Flow

1. User registers and logs in via the Gateway → Auth service issues JWT.
2. User requests conversion with a URL → Gateway validates token and enqueues job.
3. Worker downloads, converts, and uploads MP3 to MinIO → publishes event.
4. Notification service consumes event → requests a signed download token from Gateway → emails user with download link.
5. User downloads MP3 securely via Gateway → MinIO.

## Deployment

Each service has its own Dockerfile and Kubernetes manifests under `src/<service>/manifest/`.

-   Configurations are managed with **ConfigMaps** and **Secrets**.
-   Stateful services (Postgres, RabbitMQ, MinIO) use **StatefulSets** with persistent volumes.
-   Gateway is exposed via an **Ingress**.

## Development

-   Python 3.13, FastAPI, SQLModel, aio-pika, boto3, httpx.
-   Each service is independently containerized and can be run locally with Docker or deployed to Kubernetes.
-   Secrets are excluded from version control (`.gitignore`).

## Notes

-   Conversion uses `ffmpeg` inside the Worker container.
-   JWT is used for authentication and secure download tokens.
-   Email delivery is handled via the Resend API.
