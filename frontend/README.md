# WDYMEME – Frontend

This is the frontend interface for the Information Retrieval Memes Search Engine ("WDYMEME"). It provides a fast, responsive, and interactive UI for searching, filtering, and discovering topic-clustered memes indexed in Apache Solr.

## Tech Stack

- **Framework:** [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool:** [Vite](https://vite.dev/)
- **State Management:** [Pinia](https://pinia.vuejs.org/) (with persisted state)
- **Routing:** [Vue Router](https://router.vuejs.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **HTTP Client:** [Axios](https://axios-http.com/)
- **Icons:** [Lucide Vue Next](https://lucide.dev/)

---

## Frontend Directory Structure

```text
frontend/
├── public/                 # Static global assets
│   └── favicon.jpg
├── src/
│   ├── assets/             # Stylesheets and base configurations
│   │   └── main.css        # Tailwind directives and modifications
│   ├── components/         # Modular reusable layout items
│   │   ├── icons/          # Graphic assets and backgrounds
│   │   ├── sidebar/        # Component inputs (ActiveFiltersBar, FilterPanel, SearchBar, SearchInput, TagInput)
│   │   ├── LoadingComponent.vue
│   │   ├── MemeCardComponent.vue
│   │   ├── PaginationComponent.vue
│   │   └── SidebarTopics.vue
│   ├── router/             # View routing rules (index.js)
│   ├── service/            # Core Axios instances connecting to Solr (memeSearchService.js)
│   ├── stores/             # Persisted client state manager (memeSearchStore.js)
│   ├── views/              # View layer configurations (HomeView.vue, MemeListView.vue)
│   └── App.vue             # Main viewport application node
├── .env                    # Deployment environment configurations (create this!)
├── index.html              # HTML DOM scaffolding base
├── package.json            # Node configuration scripts and list tracking dependencies
└── vite.config.js          # Vite build parameters engine
```

---

## Getting Started

### 1. Prerequisites

Ensure you have [Node.js](https://nodejs.org/) (v20.19.0 or ≥22.12.0) installed on your machine.

### 2. Installation

Navigate to the `frontend` directory and install the necessary dependencies:

```bash
npm install
```

### 3. Environment Setup

The frontend needs to know how to communicate with your Solr backend. Create a `.env` file in the root of the `frontend` directory and define your Solr base path:

```env
VITE_SOLR_PATH=http://localhost:8983
```

_(Ensure your global Homebrew Solr instance is running on this port before executing searches)._

### 4. Running the Development Server

Start the Vite development server. It is configured to run on port `3000`:

```bash
npm run dev
```

Open your browser and navigate to `http://localhost:3000`.

---

## Key Features

- **Search & Filter Pipeline:** Users can search for specific titles while applying toggleable filters for Media Type (Image/Video) and specific comma-separated tags.
- **Topic Clustering Navigation:** Integrates with Solr's Lingo clustering algorithm to generate a dynamic sidebar of trending topics based on search results.
- **Persisted State:** User search queries and active filters are saved locally using `pinia-plugin-persistedstate`, ensuring they don't lose their context upon refreshing.
- **Pagination:** Handles large Solr query result sets efficiently with frontend pagination controls.

---

## Available Scripts

Here are the primary npm scripts available in this project:

| Command            | Description                                                                               |
|--------------------|-------------------------------------------------------------------------------------------|
| `npm run dev`      | Starts the development server at `http://localhost:3000`.                                 |
| `npm run build`    | Compiles and minifies the application for production deployment into the `dist/` folder.  |
| `npm run preview`  | Boots up a local web server to preview your production build.                             |
| `npm run format`   | Formats all code inside the `src/` directory using Prettier.                              |
| `npm run lint`     | Runs both ESLint and OXLint to analyze code correctness and fix auto-resolvable issues.   |
