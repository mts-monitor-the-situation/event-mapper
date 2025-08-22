FROM python:3.12-slim AS base

WORKDIR /workspace


RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY main.py requirements.txt constraints.txt ./
COPY config/ config/
COPY consumer/ consumer/
COPY geocode/ geocode/
COPY mongo/ mongo/
COPY nlp/ nlp/

RUN pip3 install --no-cache-dir -r requirements.txt -c constraints.txt


FROM python:3.12-slim AS final
WORKDIR /service
COPY --from=base /opt/venv /opt/venv
COPY --from=base /workspace ./
ENV PATH="/opt/venv/bin:$PATH"
ENTRYPOINT [ "python3", "main.py" ]
