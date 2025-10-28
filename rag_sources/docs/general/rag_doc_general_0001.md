# General Knowledge: Write a SQL query to find duplicate records

## Context
Technical knowledge and best practices.

## Response
SELECT name, email, COUNT(*) as count
FROM users
GROUP BY name, email
HAVING COUNT(*) > 1;

## Metadata
- **Domain**: general
- **Source**: unknown
- **Quality Score**: 0.50
- **Created**: 2025-10-28T06:31:09.492389