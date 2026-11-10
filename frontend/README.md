# Frontend: WDYMEME User Interface

The frontend is a responsive Single Page Application (SPA) built with **Vue.js 3** (Composition API, `<script setup>`), **Vite 7**, **Tailwind CSS v4**, and **Pinia**. It lets users search and filter memes and browse them by the topics that Apache Solr's **Carrot2 Lingo** clustering finds in the indexed data.

---

## Key Features

- **Image & Video Cards:** Each result shows its title, the image (lazy-loaded) or an HTML5 video player with controls, and its tags.
- **Title & Tag Search:** Search by title keyword (press `Enter`, click the search icon, or click **Apply**) and add tag filters as chips.
- **Media Type Filter:** Restrict results to *Image* or *Video* with checkboxes in the filter panel.
- **Topic Sidebar:** A slide-out sidebar lists the topic clusters returned by Solr's Lingo engine, with the number of memes in each. Selecting a topic limits the results to that cluster.
- **Active Filter Indicators:** A badge on the **Filter** button shows how many filters are active; below the search bar, the selected topic is shown with a **Clear all** link.
- **Persisted State:** The Pinia store is saved in `localStorage` with `pinia-plugin-persistedstate`. Topic clusters are cached there for 1 hour to avoid repeating the expensive clustering query.
- **Server-Side Pagination:** Results are loaded 12 at a time using Solr's `offset` and `limit`.

---

## Nginx Reverse Proxy (No CORS)

In the Docker setup:

- Nginx serves the built Vue app on container port `80`, published on host port `8080`.
- Solr listens on port `8983` inside the Docker network.

If the browser called Solr directly on a different port (`http://localhost:8080` → `http://localhost:8983`), it would apply **Cross-Origin Resource Sharing (CORS)** rules and block the requests, because Solr does not send CORS headers by default.

To avoid this, Nginx serves the static files and also forwards Solr requests:

```
┌─────────────────┐  Host port  ┌────────────────────────────────────────────────────────┐
│     Browser     │    8080     │                    Frontend Container                  │
│                 │ ──────────> │  Nginx (Port 80)                                       │
│                 │             │   ├── /       ───> Serves Vue static files (dist/)     │
│                 │             │   └── /solr/  ───> Proxies to http://solr:8983/solr/   │
└─────────────────┘             └───────────────────────────────────┬────────────────────┘
                                                                    │
                                                                    ▼
                                                       ┌────────────────────────┐
                                                       │  Solr (Port 8983)      │
                                                       └────────────────────────┘
```

1. **Static files:** requests to `/` are served from `dist/`; unknown paths fall back to `index.html` so client-side routes work on reload.
2. **API proxy:** every request under `/solr/` is forwarded to `http://solr:8983/solr/`.
3. **Single origin:** the browser only talks to `http://localhost:8080`, so CORS never applies.

> **Note:** the proxy forwards the whole `/solr/` path, including Solr's admin and update APIs. This is fine for local use, but restrict it to the query endpoints before exposing the app on a public network.

---

## Directory Structure

```text
frontend/
├── .editorconfig                # Editor settings
├── .prettierrc.json             # Prettier configuration (with Tailwind plugin)
├── Dockerfile                   # Multi-stage build (Node.js build -> Nginx runtime)
├── README.md                    # Frontend documentation
├── eslint.config.js             # ESLint 9 flat config with Oxlint and Prettier integration
├── index.html                   # HTML entry point (page title "WDYMEME")
├── jsconfig.json                # Path alias (@ -> src)
├── nginx.conf                   # Nginx static file server & reverse proxy
├── package.json                 # Dependencies and npm scripts
├── package-lock.json
├── public/
│   └── favicon.jpg              # Favicon
├── src/
│   ├── App.vue                  # Root component (renders the router view)
│   ├── assets/
│   │   └── main.css             # Tailwind CSS v4 entry point
│   ├── components/
│   │   ├── LoadingComponent.vue     # Animated loading spinner
│   │   ├── MemeCardComponent.vue    # Meme card (image/video and tags)
│   │   ├── PaginationComponent.vue  # Page navigation buttons
│   │   ├── SidebarTopics.vue        # Slide-out sidebar with Lingo topics
│   │   ├── icons/
│   │   │   └── background.png       # Home page background image
│   │   └── sidebar/                 # Search bar and filter components
│   │       ├── ActiveFiltersBar.vue # Selected topic badge and "Clear all" link
│   │       ├── FilterPanel.vue      # Media type and tag filters
│   │       ├── SearchBar.vue        # Search bar (input + filters + menu button)
│   │       ├── SearchInput.vue      # Title search input with filter button
│   │       └── TagInput.vue         # Comma-separated tag input
│   ├── main.js                  # App bootstrap (Vue, Pinia + persistence, Router)
│   ├── router/
│   │   └── index.js             # Routes: / and /meme-list
│   ├── service/
│   │   └── memeSearchService.js # Axios client for Solr search and clustering queries
│   ├── stores/
│   │   └── memeSearchStore.js   # Pinia store with persisted search state
│   └── views/
│       ├── HomeView.vue         # Landing page with the search bar
│       └── MemeListView.vue     # Results page
└── vite.config.js               # Vite config (Vue, Vue DevTools, Tailwind, dev proxy)
```

---

## Components & Architecture

### Routes

| Path         | Name            | View               |
|:-------------|:----------------|:-------------------|
| `/`          | `Home`          | `HomeView.vue`     |
| `/meme-list` | `List of memes` | `MemeListView.vue` |

### Views

- **`HomeView.vue`**: Full-screen landing page with a background image and the central search bar (title search and filter panel). Running a search navigates to `/meme-list`.
- **`MemeListView.vue`**: Results page. A sticky search bar sits at the top, with a menu button that opens the topic sidebar. Results are shown in a responsive grid (1, 2, or 3 columns) of `MemeCardComponent` items, with a loading spinner, a "no results" message, and pagination below.

### State Management (`memeSearchStore.js`)

Pinia store `memes`, persisted entirely in `localStorage`:

- `query`: current title search keyword.
- `filters`: active filters, keyed by option id: `'1'` = image, `'2'` = video, `'3'` = array of tags.
- `results`: memes on the current page.
- `found_docs`: total number of matching documents.
- `start`: offset of the current page.
- `loading`: whether a search is running.
- `all_clusters`: topic clusters returned by Solr.
- `selected_cluster`: the topic currently used as a filter.
- `last_cluster_fetch`: time of the last cluster fetch (clusters are refreshed after 1 hour).

### API Service (`memeSearchService.js`)

All requests go to `${VITE_SOLR_PATH}/solr/memes_collection/select`.

- **`fetchClusters()`**: `GET` with `q=*:*`, `rows=100000`, `clustering=true` and `clustering.engine=lingo`; returns the `clusters` array.
- **`searchForAMeme(title, media_type, tags, start, cluster_docs)`**: `POST` using Solr's JSON Request API:
  - `query`: `title:<keyword>`, or `*:*` if empty
  - `filter`: `media_type:<image|video>`, `tags:<tags>` (selected tags joined by commas), and `{!terms f=id}<id1,id2,...>` for the selected topic
  - `offset`: `start`; `limit`: `12`

---

## Environment Variables

| Variable         | Description                                                                                          | Docker build        | Local development   |
|:-----------------|:-----------------------------------------------------------------------------------------------------|:--------------------|:--------------------|
| `VITE_SOLR_PATH` | Base URL prepended to Solr requests. When empty or unset, requests use the relative path `/solr/...`. | `""` (empty string) | Unset (uses the Vite proxy) |

`VITE_SOLR_PATH` is read at **build time**; changing it requires rebuilding the app.

---

## Local Development (Without Docker)

To run the frontend with Hot Module Replacement (HMR):

### 1. Prerequisites

- **Node.js** `^20.19.0` or `>=22.12.0`
- **npm** `v10+`
- A running Solr instance with an indexed `memes_collection` (for example `docker compose up solr -d` plus the backend pipeline).

### 2. Install Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Development Server

```bash
npm run dev
```

The app is served at [http://localhost:3000](http://localhost:3000). The Vite dev server forwards every `/solr` request to `http://localhost:8983`, the same way Nginx does in production, so the browser does not hit CORS errors. To proxy to a different Solr instance:

```bash
SOLR_PROXY_TARGET="http://my-solr-host:8983" npm run dev
```

> Do not set `VITE_SOLR_PATH=http://localhost:8983` for local development: the browser would call Solr on another origin and the requests would be blocked by CORS.

---

## Available Scripts

| Command               | Description                                                        |
|:----------------------|:-------------------------------------------------------------------|
| `npm run dev`         | Starts the Vite dev server on port `3000`.                         |
| `npm run build`       | Builds the production bundle into `dist/`.                         |
| `npm run preview`     | Serves the built `dist/` folder locally.                           |
| `npm run lint`        | Runs `lint:oxlint` and then `lint:eslint` (both auto-fix).         |
| `npm run lint:oxlint` | Runs Oxlint correctness rules with auto-fix.                       |
| `npm run lint:eslint` | Runs ESLint on Vue and JavaScript files with caching and auto-fix. |
| `npm run format`      | Formats all files in `src/` with Prettier.                         |

---

## Docker Production Build

The frontend image is built in two stages:

1. **Build stage (`node:20-alpine`):** installs the npm dependencies and runs `npm run build` with `VITE_SOLR_PATH=""`.
2. **Runtime stage (`nginx:alpine`):** copies `dist/` to `/usr/share/nginx/html` and `nginx.conf` to `/etc/nginx/conf.d/default.conf`.

The Nginx config proxies to the hostname `solr`, so the container must run on the same Docker network as the Solr service. The simplest way is through Docker Compose from the repository root:

```bash
docker compose up --build frontend
```
