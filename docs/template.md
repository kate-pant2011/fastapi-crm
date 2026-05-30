# Topic / Feature

## Overview
Краткий список того, что реализовано

## Goal
Зачем это нужно?
Какую проблему решает?

---

## Endpoints
Список эндпоинтов

---

## How It Works
Как это работает?
Как проходит логика?
Что из чего вытекает?
logic, flow, structure, instructions

---

## Architecture Decisions
Описать архитектурное решение

Пример:
project structure
layered structure
async/sync
auth strategy
background tasks
caching
dependency injection
queue system
dockerized environment
file storage strategy (Cloud Storage, Local Storage, DB Storage)
database strategy (asyncpg, sqlalchemy, alembic, sort, soft delete...)
communication between components(smtp service, file storage, router, auth system, celery worker...)

---

## Request Flow
как запрос проходит через систему
Router→ Depends(auth) → Service → Database→ Response

---

## Validation rules
Как и где валидируются данные?
Например: 
Pydantic schemas
custom validators
constraints in DB
type validation
email validation
business validation

---

## Security Considerations
Какие аспекты безопасности используются? 
Например: 
passwords hashed;
JWT expiration;
protected endpoints;
role checks;
secret keys;
refresh token strategy.

---

## Why This Approach
Почему именно такое архитектурное решение?

---

## Alternatives Considered
Какие были альтернативы?

---

## Problems / Difficulties
С чем возникли сложности?

---

## Possible Improvements
Что пока не реализовано? 
Что нужно доделать?
Что хочется улучшить?

---
