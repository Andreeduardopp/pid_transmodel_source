# ============================================================
# Dockerfile — Monolito Django (GeoDjango + PostGIS)
# ============================================================
# Imagem base com GDAL/GEOS/PROJ pré-instalados para GeoDjango
FROM python:3.12-slim AS base

# Variáveis de ambiente para Python/Django
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dependências de sistema necessárias para GeoDjango (GDAL, GEOS, PROJ)
# e para psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
        binutils \
        gdal-bin \
        libgdal-dev \
        libgeos-dev \
        libproj-dev \
        libpq-dev \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# Etapa de dependências
# ============================================================
FROM base AS deps

WORKDIR /app

# Instalar uv para gerenciar dependências
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copiar arquivos de dependência primeiro (cache de camada)
COPY pyproject.toml uv.lock ./

# Instalar dependências do projeto (sem instalar o projeto em si)
RUN uv sync --frozen --no-install-project

# ============================================================
# Etapa final
# ============================================================
FROM base AS final

WORKDIR /app

# Copiar o virtualenv criado pelo uv
COPY --from=deps /app/.venv /app/.venv

# Garantir que o PATH aponte para o virtualenv
ENV PATH="/app/.venv/bin:$PATH"

# Copiar código-fonte do projeto
COPY . .

# Expor porta padrão do Django/Gunicorn
EXPOSE 8000

# Coletar arquivos estáticos (em produção)
RUN python monolito/manage.py collectstatic --noinput 2>/dev/null || true

# Healthcheck básico
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/admin/')" || exit 1

# Iniciar com Gunicorn apontando para o WSGI do Django
CMD ["gunicorn", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", \
     "--timeout", "120", \
     "--chdir", "monolito", \
     "sistema_fretamento.wsgi:application"]
