# 1Panel Docker Deployment Guide

This project now supports direct Docker image deployment with SQLite persistence and bundled media sync.

## What is included

- `Dockerfile`: production image based on Python 3.12
- `docker/entrypoint.sh`: auto-migrate, auto-collectstatic, auto-seed bundled media, optional superuser creation
- `docker-compose.yml`: ready for 1Panel Compose deployment
- `.env.example`: environment variable template
- `.github/workflows/docker-image.yml`: auto-build and push image to GHCR

## Persistence design

This project uses SQLite and local media files:

- SQLite database: stored at `/data/db.sqlite3`
- Media directory: stored at `/data/media`
- Docker volume: mounted to `/data`

The repository already contains many PDF files in `media/`. To avoid losing them after mounting a persistent volume, the container startup script copies missing bundled media files from the image into `/data/media` on every boot.

This means:

- existing built-in PDFs remain available
- uploaded avatars are persisted
- SQLite data is persisted
- new bundled media files added in later image versions are copied in automatically

## Environment variables

Copy `.env.example` to `.env` and update it:

```bash
cp .env.example .env
```

Important variables:

- `IMAGE_NAME`: the remote image to pull
- `APP_PORT`: host port exposed by Docker
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: your domain, comma-separated
- `CSRF_TRUSTED_ORIGINS`: full origin list such as `https://course.example.com`
- `DJANGO_LOAD_SAMPLE_DATA`: `1` to auto-load initial subject/question data when the database is empty
- `DJANGO_SUPERUSER_USERNAME`: optional admin username created at startup
- `DJANGO_SUPERUSER_PASSWORD`: optional admin password created at startup

## Option A: manual image build and push

Use this if you want to push an image yourself from your local machine.

### 1. Log in to GHCR

```bash
docker login ghcr.io
```

Use:

- username: your GitHub username
- password: a GitHub Personal Access Token with `write:packages`

### 2. Build the image

Replace `your-org` with your GitHub organization name.

```bash
docker build -t ghcr.io/your-org/ts-alevel-courser:latest .
```

You can also push a version tag:

```bash
docker tag ghcr.io/your-org/ts-alevel-courser:latest ghcr.io/your-org/ts-alevel-courser:2026-04-23
```

### 3. Push the image

```bash
docker push ghcr.io/your-org/ts-alevel-courser:latest
docker push ghcr.io/your-org/ts-alevel-courser:2026-04-23
```

## Option B: automatic build and push with GitHub Actions

The repository now includes `.github/workflows/docker-image.yml`.

It will build and push images to:

```text
ghcr.io/<owner>/<repo>
```

Triggers:

- push to `main`
- push to `master`
- git tags starting with `v`
- manual run from GitHub Actions

Generated tags include:

- `latest` on the default branch
- branch name
- git tag
- commit SHA

### Required GitHub settings

1. Push this repository change to GitHub.
2. Ensure GitHub Actions is enabled for the repository.
3. Ensure your organization allows publishing packages to GHCR.
4. If the package should be pulled without login from 1Panel, set the package visibility to public.

If you keep the package private, configure 1Panel with registry credentials for `ghcr.io`.

## Deploy on 1Panel

### Method 1: use Compose in 1Panel

1. On the server, create a new directory such as:

```bash
mkdir -p /opt/1panel/apps/ts-alevel-courser
cd /opt/1panel/apps/ts-alevel-courser
```

2. Upload these two files from the repo:

- `docker-compose.yml`
- `.env` based on `.env.example`

3. Edit `.env`:

```env
IMAGE_NAME=ghcr.io/your-org/ts-alevel-courser:latest
APP_PORT=8000
SECRET_KEY=replace-with-a-random-secret
DEBUG=0
ALLOWED_HOSTS=course.example.com
CSRF_TRUSTED_ORIGINS=https://course.example.com
DJANGO_LOAD_SAMPLE_DATA=1
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=replace-with-a-strong-password
DJANGO_SUPERUSER_EMAIL=admin@example.com
```

4. In 1Panel:

- open `Containers`
- choose `Compose`
- create a compose project
- point it to this directory or paste the contents of `docker-compose.yml`
- start the project

5. Configure the 1Panel website reverse proxy:

- domain: `course.example.com`
- target: `127.0.0.1:8000` or the compose service port
- enable HTTPS

After startup:

- app: `https://course.example.com/`
- admin: `https://course.example.com/admin/`
- health check: `https://course.example.com/healthz/`

### Method 2: create a single container in 1Panel

If you prefer not to use Compose:

1. Create a container from image `ghcr.io/your-org/ts-alevel-courser:latest`
2. Map port `8000` in the container to a host port such as `8000`
3. Add a persistent volume:

```text
Host path or named volume -> /data
```

4. Add the same environment variables from `.env.example`
5. Start the container
6. Use a 1Panel reverse proxy to expose the service

## Updating after code changes

### If you use manual push

1. Commit your code changes
2. Rebuild the image
3. Push the new tag
4. In 1Panel, pull the new image and recreate the container

### If you use GitHub Actions

1. Commit and push to `main`
2. Wait for the GitHub Actions workflow to finish
3. In 1Panel, redeploy the compose app or recreate the container using the new image

Because the volume is mounted to `/data`, these survive upgrades:

- SQLite database
- uploaded avatars
- copied media files

## Recommended release workflow

For stable upgrades, use immutable tags instead of relying only on `latest`.

Example:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then set:

```env
IMAGE_NAME=ghcr.io/your-org/ts-alevel-courser:v1.0.0
```

When upgrading:

1. build and publish `v1.0.1`
2. change `IMAGE_NAME` in 1Panel
3. redeploy

This is safer than pulling an always-moving `latest`.

## Local verification

Build locally:

```bash
docker build -t ts-alevel-courser:local .
```

Run locally:

```bash
docker run --rm -p 8000:8000 \
  -e SECRET_KEY=dev-secret \
  -e DEBUG=0 \
  -e ALLOWED_HOSTS=localhost,127.0.0.1 \
  -e CSRF_TRUSTED_ORIGINS=http://localhost:8000 \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_PASSWORD=admin123 \
  -v ts_alevel_courser_data:/data \
  ts-alevel-courser:local
```

## Notes

- SQLite is suitable here because concurrency is low.
- Media is served by Django in production for simplicity. This is acceptable for a small internal deployment.
- If later traffic grows, you can move media delivery to Nginx or object storage without changing the persistence layout.
