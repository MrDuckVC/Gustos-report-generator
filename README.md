# Gustos Report Generator

## Installation

1. Create and fill files:
    - database.env based on database.env.dev
    - backend.env based on backend.env.dev
    - docker-compose.override.yml based on docker-compose.override-dev.yml
2. Input gutos database dump in `docker/db/docker-entrypoint-initdb.d`
3. Run `docker-compose up -d --build`
4. Run `docker-compose run backend python manage.py migrate`
5. Run `docker-compose run backend python manage.py collectstatic`
6. Run `docker-compose restart backend`
