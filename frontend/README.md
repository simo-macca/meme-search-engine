# Frontend User Interface

The frontend is a modern, responsive Single Page Application (SPA) built with **Vue.js 3** (Composition API, `<script setup>`), **Vite 7**, and **Tailwind CSS v4**. It provides a reactive interface for searching, filtering, and exploring memes grouped by semantic topics discovered dynamically through Apache Solr's **Carrot2 Lingo** clustering algorithm.

---

## Key Features

- **Multimodal Meme Rendering:** Automatically detects and displays images and HTML5 videos (with autoplay, loop, and playback controls).
- **Full-Text & Tag Search:** Instant title query search combined with multi-tag filtering chips.
- **Media Type Filtering:** Quick toggle between *All*, *Images*, and *Videos*.
- **Dynamic Topic Exploration:** Interactive cluster sidebar populated by Solr's Lingo clustering engine, allowing users to browse memes grouped by conceptual themes.
- **Active Filter Bar:** Visual badges for all applied queries, tags, media types, and active topic clusters with single-click removal.
- **Client-Side State Persistence:** Powered by **Pinia** and `pinia-plugin-persistedstate` to persist search state, active filters, and an in-memory 1-hour cache for clustering results to reduce heavy Solr queries.
- **Server-Side Pagination:** Efficient 12-item pagination using Solr's `start` (offset) and `rows` (limit).

---

## The Nginx Reverse Proxy & CORS Resolution

When running the application in production via Docker:
- The Vue UI is served on port `8080`.
- The Solr backend listens internally on port `8983`.

If the browser makes requests directly across different ports (`http://localhost:8080` to `http://localhost:8983`), modern browsers enforce strict **Cross-Origin Resource Sharing (CORS)** policies and block the requests unless complex headers are configured on Solr.

To eliminate CORS without exposing Solr to security risks, the production Docker container wraps the built Vue static assets in an **Nginx** server:

```
┌─────────────────┐             ┌────────────────────────────────────────────────────────┐
│     Browser     │  Port 8080  │                    Frontend Container                  │
│                 │ ──────────> │  Nginx (Port 80)                                       │
│                 │             │   ├── /       ───> Serves Vue Static Files (dist/)     │
│                 │             │   └── /solr/  ───> Proxies to http://solr:8983/solr/   │
└─────────────────┘             └───────────────────────────────────┬────────────────────┘
                                                                    │
                                                                    ▼
                                                       ┌────────────────────────┐
                                                       │ Solr Cloud (Port 8983) │
                                                       └────────────────────────┘
```

1. **Nginx serves the SPA:** All frontend requests (`/`) serve `dist/index.html`.
2. **Nginx proxies API requests:** Any request directed to `/solr/` is reverse-proxied internally to `http://solr:8983/solr/`.
3. **Zero CORS:** The browser communicates exclusively with origin `http://localhost:8080`, entirely bypassing browser CORS limitations.

---

## Directory Structure

```text
frontend/
├── Dockerfile                   # Multi-stage Docker build (Node.js build -> Nginx runtime)
├── README.md                    # Frontend documentation
├── eslint.config.js             # ESLint 9 configuration with Oxlint and Prettier integration
├── index.html                   # HTML entry point
├── jsconfig.json                # Path mapping aliases (@ -> src)
├── nginx.conf                   # Production Nginx reverse-proxy & static file server
├── package.json                 # Dependencies and npm scripts
├── package-lock.json
├── public/
│   └── favicon.jpg              # Application favicon
├── src/
│   ├── App.vue                  # Root application component
│   ├── assets/
│   │   └── main.css             # Tailwind CSS v4 entry point
│   ├── components/
│   │   ├── LoadingComponent.vue # Animated loading spinner
│   │   ├── MemeCardComponent.vue# Meme card with image/video rendering & tag badges
│   │   ├── PaginationComponent.vue# Page navigation controls
│   │   ├── SidebarTopics.vue    # Lingo cluster topic list sidebar
│   │   ├── icons/
│   │   │   └── background.png   # Hero background asset
│   │   └── sidebar/
│   │       ├── ActiveFiltersBar.vue # Active filter badges with dismiss buttons
│   │       ├── FilterPanel.vue      # Filter controls (media type, tags)
│   │       ├── SearchBar.vue        # Search bar wrapper
│   │       ├── SearchInput.vue      # Text input for title queries
│   │       └── TagInput.vue         # Chip-based tag input
│   ├── main.js                  # Application bootstrapper (Vue, Pinia, Router)
│   ├── router/
│   │   └── index.js             # Vue Router route definitions (/ and /memes)
│   ├── service/
│   │   └── memeSearchService.js # Axios client for Solr /select queries and clustering
│   ├── stores/
│   │   └── memeSearchStore.js   # Pinia store with persisted search and filter state
│   └── views/
│       ├── HomeView.vue         # Landing hero page with search and popular topics
│       └── MemeListView.vue     # Search results view with sticky sidebar and grid
└── vite.config.js               # Vite 7 build configuration with Tailwind and Vue plugins
```

---

## Component & Architecture Overview

### Views
- **`HomeView.vue`**: Clean landing page featuring an animated hero banner, central search bar, quick filter options, and instant topic cluster suggestions.
- **`MemeListView.vue`**: The main exploration workspace. Features a sticky sidebar containing filters and dynamic Lingo topics on the left, an active filters bar on top, a responsive grid of `MemeCardComponent` items in the center, and pagination controls at the bottom.

### State Management (`memeSearchStore.js`)
Uses **Pinia** with state persistence (`pinia-plugin-persistedstate`):
- `query`: Current title search keyword.
- `filters`: Active media type (`1` = image, `2` = video) and tag array.
- `results`: Current page array of meme documents returned from Solr.
- `found_docs`: Total matching documents count in Solr.
- `start`: Pagination offset.
- `all_clusters`: Cached topic clusters from Solr.
- `selected_cluster`: Currently active cluster filter.
- `last_cluster_fetch`: Timestamp for 1-hour cluster cache invalidation.

### API Service (`memeSearchService.js`)
- **`fetchClusters()`**: Queries Solr with `q=*:*`, `rows=100000`, `clustering=true`, and `clustering.engine=lingo` to retrieve discovered topic clusters.
- **`searchForAMeme(title, media_type, tags, start, cluster_docs)`**: Dispatches a Solr JSON query with optional filters:
  - Title text search: `title:<keyword>` (or `*:*`)
  - Media type filter: `media_type:image` or `media_type:video`
  - Tag filter: `tags:<tag>`
  - Cluster restriction: `{!terms f=id}<doc1,doc2,...>`
  - Pagination: `offset: start`, `limit: 12`

---

## Environment Variables

| Variable         | Description                                                                                        | Docker Production   | Local Dev Default       |
|:-----------------|:---------------------------------------------------------------------------------------------------|:--------------------|:------------------------|
| `VITE_SOLR_PATH` | Base URL for Solr requests. When empty, requests use relative path `/solr/...` (proxied by Nginx). | `""` (empty string) | `http://localhost:8983` |

---

## Local Development (Without Docker)

To run the frontend locally with Hot Module Replacement (HMR) enabled:

### 1. Prerequisites
- **Node.js**: `^20.19.0` or `>=22.12.0`
- **npm**: `v10+`
- A running Solr instance with `memes_collection` (e.g., started via `docker compose up solr -d`).

### 2. Installation
```bash
cd frontend
npm install
```

### 3. Run Development Server
Provide `VITE_SOLR_PATH` pointing to your local Solr port (`8983`):

```bash
VITE_SOLR_PATH="http://localhost:8983" npm run dev
```

The Vite dev server will start at:
```text
http://localhost:3000
```

---

## Available Scripts

| Command               | Description                                               |
|:----------------------|:----------------------------------------------------------|
| `npm run dev`         | Starts the Vite development server on port `3000`.        |
| `npm run build`       | Compiles and bundles production static assets to `dist/`. |
| `npm run preview`     | Serves the locally built `dist/` directory for preview.   |
| `npm run lint`        | Runs both `oxlint` and `eslint` with automatic fixes.     |
| `npm run lint:oxlint` | Runs fast Oxlint correctness checks.                      |
| `npm run lint:eslint` | Runs ESLint on Vue and JavaScript files with caching.     |
| `npm run format`      | Formats all files in `src/` using Prettier.               |

---

## Docker Production Build

The frontend is containerized using a two-stage build:
1. **Build Stage (`node:20-alpine`):** Installs npm dependencies and runs `npm run build` with `VITE_SOLR_PATH=""`.
2. **Production Stage (`nginx:alpine`):** Copies static files from `/app/dist` to `/usr/share/nginx/html` and mounts `nginx.conf`.

To build and run the frontend container independently:
```bash
docker build -t meme-frontend ./frontend
docker run -p 8080:80 --name meme_frontend meme-frontend
```
