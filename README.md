# ⚡ Async Order Processing & Microservices

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

Microservicio backend asíncrono diseñado para la ingesta y persistencia transaccional (ACID) de órdenes de compra de alta concurrencia. Implementa control de tráfico por IP/Token con Redis y autenticación criptográfica JWT (OAuth2).

---

## 1. Problema de Negocio

Los sistemas monolíticos síncronos presentan cuellos de botella I/O ante picos de concurrencia, generando bloqueos en pools de conexiones, inconsistencia en transacciones financieras y vulnerabilidad ante ataques de denegación de servicio (DoS). 

**Solución Implementada:**
* **Saturación I/O Bloqueante:** Implementación de Event Loop asíncrono con FastAPI y el driver `asyncpg`.
* **Abuso de API & Fuerza Bruta:** Middleware distribuido de *Rate Limiting* (Token Bucket) sobre Redis.
* **Integridad Transaccional:** Esquema relacional normalizado con persistencia atómica en dos fases (`orders` y `order_items`).

---

## 2. Arquitectura del Sistema

### Arquitectura Global
![Arquitectura Global](Async%20Order-2026-08-18-212950.png)

### Flujo de Datos (ETL & API)
```mermaid
flowchart TD
    subgraph CLIENT_LAYER ["1. Ingesta & Clientes"]
        CLI[Cliente HTTP / Load Tester]
        LOAD[Tráfico Concurrente]
    end

    subgraph SECURITY_LAYER ["2. DevSecOps & Control de Tráfico"]
        AUTH[OAuth2 Bearer / JWT HS256]
        RL[Redis Rate Limiter\nToken Bucket]
    end

    subgraph APP_LAYER ["3. Capa de Aplicación (FastAPI Async)"]
        ROUTER[API Router /api/v1]
        SVC[Order Domain Service]
        REPO[Repository Layer / SQLAlchemy 2.0]
    end

    subgraph STORAGE_LAYER ["4. Persistencia ACID & Cache"]
        REDIS[(Redis 7.x\nCluster Cache)]
        PG[(PostgreSQL 15+\nEngine asyncpg)]
    end

    CLI -->|POST /login| AUTH
    CLI -->|POST /orders| AUTH
    AUTH -->|Filtro IP / Token| RL
    RL <-->|INCR / EXPIRE Atómico| REDIS
    RL -->|Tráfico Autorizado| ROUTER
    ROUTER --> SVC
    SVC --> REPO
    REPO -->|BEGIN / COMMIT ACID| PG

    classDef infra fill:#1e293b,stroke:#0284c7,stroke-width:2px,color:#fff;
    classDef app fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff;
    classDef sec fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff;
    class CLIENT_LAYER,STORAGE_LAYER infra;
    class APP_LAYER app;
    class SECURITY_LAYER sec;
