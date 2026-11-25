FROM python:3.12-slim

# uv for fast, locked installs
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /artifact

# Install dependencies first so the layer is cached across data changes
COPY analysis_utils/ analysis_utils/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Then the analysis code, notebooks and data
COPY notebooks/      notebooks/
COPY data/           data/
COPY packets/        packets/
COPY images/         images/
COPY rendered/       rendered/
COPY README.md APPS.md ./

EXPOSE 8888

# JupyterLab, no token, reachable from the host
CMD ["uv", "run", "jupyter", "lab", "--ip=0.0.0.0", "--port=8888", \
     "--no-browser", "--allow-root", "--ServerApp.token=", "--ServerApp.password=", "--ServerApp.disable_check_xsrf=True"]