FROM python:3.12.4-alpine3.20



COPY ./requirements /requirements
COPY ./Scripts /Scripts

COPY ./edue /src

WORKDIR src

EXPOSE 8000

RUN /py/bin/pip install  -r /requirements/development.txt


RUN chmod -R +x /Scripts && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    adduser --disabled-password --no-create-home marketshop && \
    chown -R marketshop:marketshop /vol && \
    chmod -R 755 /vol


ENV PATH="/Scripts:/py/bin:$PATH"
ENV PYTHONPATH="/src/config"

USER marketshop

CMD ["run.sh"]