# iris-docker-multi-stage-script

A python script to keep your iris images in shape ;)

## Usage

First have a look at a non-multi-stage Dockerfile for iris:

```dockerfile
ARG IMAGE=intersystemsdc/irishealth-community:latest
FROM $IMAGE 

WORKDIR /irisdev/app
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /irisdev/app
USER ${ISC_PACKAGE_MGRUSER}

# copy source code
COPY src src
COPY misc misc
COPY data/fhir fhirdata
COPY iris.script /tmp/iris.script
COPY fhirUI /usr/irissys/csp/user/fhirUI

# run iris and initial 
RUN iris start IRIS \
	&& iris session IRIS < /tmp/iris.script \
	&& iris stop IRIS quietly
```

This is a simple Dockerfile that will build an image with the iris source code and the fhir data. It will also run the iris.script to create the fhir database and load the data.

With this kind of dockerfile you will end up with a big image. This is not a problem if you are using a CI/CD pipeline to build your images. But if you are using this image in production you will end up with a big image that will take a lot of space on your server.

Then have a look at a multi-stage Dockerfile for iris

```dockerfile
ARG IMAGE=intersystemsdc/irishealth-community:latest
FROM $IMAGE as builder

WORKDIR /irisdev/app
RUN chown ${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} /irisdev/app
USER ${ISC_PACKAGE_MGRUSER}

# copy source code
COPY src src
COPY misc misc
COPY data/fhir fhirdata
COPY iris.script /tmp/iris.script
COPY fhirUI /usr/irissys/csp/user/fhirUI

# run iris and initial 
RUN iris start IRIS \
	&& iris session IRIS < /tmp/iris.script \
	&& iris stop IRIS quietly

# copy data from builder
FROM $IMAGE

ADD --chown=${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} https://github.com/grongierisc/iris-docker-multi-stage-script/releases/latest/download/copy-data.py /irisdev/app/copy-data.py

RUN --mount=type=bind,source=/,target=/builder/root,from=builder \
	cp -f /builder/root/usr/irissys/iris.cpf /usr/irissys/iris.cpf && \
	python3 /irisdev/app/copy-data.py -c /usr/irissys/iris.cpf -d /builder/root/ 
```

This is a multi-stage Dockerfile that will build an image with the iris source code and the fhir data. It will also run the iris.script to create the fhir database and load the data. But it will also copy the data from the builder image to the final image. This will reduce the size of the final image.

Let read in details the multi-stage Dockerfile:

```dockerfile
FROM $IMAGE
```

Start with the base image

```dockerfile
ADD --chown=${ISC_PACKAGE_MGRUSER}:${ISC_PACKAGE_IRISGROUP} https://github.com/grongierisc/iris-docker-multi-stage-script/releases/latest/download/copy-data.py /irisdev/app/copy-data.py
```

Add the copy-data.py script to the image with the right user and group

```dockerfile
RUN --mount=type=bind,source=/,target=/builder/root,from=builder \
    cp -f /builder/root/usr/irissys/iris.cpf /usr/irissys/iris.cpf && \
    python3 /irisdev/app/copy-data.py -c /usr/irissys/iris.cpf -d /builder/root/ 
```

A lot is happening here. 

First we are using the --mount option to mount the builder image. 
- --mount=type=bind is the type of mount
- source=/ is the root of the builder image
- target=/builder/root is the root of the final image
- from=builder is the name of the builder image

Then we are copying the iris.cpf file from the builder image to the final image. 

```bash
cp -f /builder/root/usr/irissys/iris.cpf /usr/irissys/iris.cpf
```

Finally we are running the copy-data.py script to copy the data from the builder image to the final image.

```bash
python3 /irisdev/app/copy-data.py -c /usr/irissys/iris.cpf -d /builder/root/ 
```