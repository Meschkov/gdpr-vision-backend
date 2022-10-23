# Run Makefile like this:
# make TAG=0.0.1 cloudrun
cloudrun:  build push deploy use_latest_revision

# Basic config
$(eval PROJECT_ID = $(shell gcloud config get-value project))
CONTAINER = containername
SERVICE = cloudrunservicename

build:
	docker buildx build \
		--platform linux/amd64 . \
		--tag gcr.io/$(PROJECT_ID)/$(CONTAINER):$(TAG)

push:
	docker push gcr.io/$(PROJECT_ID)/$(CONTAINER):$(TAG)

deploy:
	gcloud run deploy $(SERVICE) \
		--image gcr.io/$(PROJECT_ID)/$(CONTAINER):$(TAG)

use_latest_revision:
	gcloud run services update-traffic $(SERVICE) --to-revisions LATEST=100