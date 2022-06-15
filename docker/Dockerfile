# Define global args
ARG FUNCTION_DIR="/home/app/"
ARG RUNTIME_VERSION="3.8"
ARG DISTRO_VERSION="3.12"

# Stage 1 - bundle base image + runtime
# Grab a fresh copy of the image and install GCC
FROM python:${RUNTIME_VERSION}-alpine${DISTRO_VERSION} AS python-alpine
# Install GCC (Alpine uses musl but we compile and link dependencies with GCC)
RUN apk add --no-cache \
    libstdc++

# Stage 2 - build function and dependencies
FROM python-alpine AS build-image
# Install aws-lambda-cpp build dependencies
RUN apk add --no-cache \
    build-base \
    libtool \
    autoconf \
    automake \
    libexecinfo-dev \
    make \
    cmake \
    libcurl \
    py3-mysqlclient
# Include global args in this stage of the build
ARG FUNCTION_DIR
ARG RUNTIME_VERSION
# Create function directory
RUN mkdir -p ${FUNCTION_DIR}

ENV RUNTIME_VERSION="${RUNTIME_VERSION}"
ENV PIGNUS_MIGRATIONS_PATH="/home/app/Pignus-py3.8.egg/pignus/migrations"

# Install Pignus
RUN mkdir -p ${FUNCTION_DIR}/pignus_build
COPY pignus/src ${FUNCTION_DIR}/pignus_build
COPY pignus/src/migrations /migrations

# RUN chmod 755 /usr/bin/aws-lambda-rie /entrypoint.sh

RUN cd ${FUNCTION_DIR}pignus_build && \
    python${RUNTIME_VERSION} -m pip install -r requirements.txt --target ${FUNCTION_DIR} && \
    python${RUNTIME_VERSION} -m pip install -r requirements.txt && \
    python${RUNTIME_VERSION} setup.py build  && \
    python${RUNTIME_VERSION} setup.py install --install-lib ${FUNCTION_DIR} && \
    mv ${FUNCTION_DIR}/Pignus-*-py3.8.egg ${FUNCTION_DIR}/Pignus-py3.8.egg

# Copy handler function
COPY src/* ${FUNCTION_DIR}
# Optional – Install the function's dependencies
# RUN python${RUNTIME_VERSION} -m pip install -r ${FUNCTION_DIR}requirements.txt --target ${FUNCTION_DIR}
# Install Lambda Runtime Interface Client for Python
RUN python${RUNTIME_VERSION} -m pip install awslambdaric --target ${FUNCTION_DIR}


# Stage 3 - final runtime image
# Grab a fresh copy of the Python image
FROM python-alpine
# Include global arg in this stage of the build
ARG FUNCTION_DIR
# Set working directory to function root directory
WORKDIR ${FUNCTION_DIR}
ENV PYTHONPATH="${PYTHONPATH}:/home/app/Pignus-py3.8.egg"
ENV PIGNUS_MIGRATIONS_PATH="/migrations"
# Copy in the built dependencies
COPY --from=build-image ${FUNCTION_DIR} ${FUNCTION_DIR}
COPY --from=build-image /migrations /migrations
# (Optional) Add Lambda Runtime Interface Emulator and use a script in the ENTRYPOINT for simpler local runs
# ADD https://github.com/aws/aws-lambda-runtime-interface-emulator/releases/latest/download/aws-lambda-rie /usr/bin/aws-lambda-rie
COPY entrypoint.sh /
# RUN chmod 755 /usr/bin/aws-lambda-rie /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "app.handler" ]
