import { defineStore } from 'pinia'
import { fetchClusters, searchForAMeme } from '@/service/memeSearchService'

export const useMemeStore = defineStore('memes', {
  state: () => ({
    query: '',
    filters: {},
    results: [],
    found_docs: 0,
    start: 0,
    loading: false,
    all_clusters: [],
    selected_cluster: null,
    last_cluster_fetch: 0,
  }),

  persist: true,

  actions: {
    async loadClusters() {
      const now = Date.now()
      const MAX_AGE = 60 * 60 * 1000

      if (this.all_clusters.length > 0 && now - this.last_cluster_fetch < MAX_AGE) {
        console.log('⚡ Clusters loaded instantly from cache')
        return
      }

      console.log('🌐 Fetching fresh clusters from Solr...')
      const data = await fetchClusters()

      this.all_clusters = data || []
      this.last_cluster_fetch = now

      console.log('✔ Clusters refreshed at:', new Date(now).toLocaleTimeString())
    },

    async performSearch() {
      this.loading = true
      console.log('🔍 Executing search...')

      try {
        const mediaType = this.filters['1'] ? 'image' : this.filters['2'] ? 'video' : null

        const tags = this.filters['3']?.join(',') ?? null
        const cluster_docs = this.selected_cluster?.docs ?? null

        const data = await searchForAMeme(this.query, mediaType, tags, this.start, cluster_docs)

        this.results = data.response.docs
        this.found_docs = data.response.numFound
        this.start = data.response.start
        console.log('✔️ Search completed successfully')
      } catch (err) {
        console.error('❌ Search failed:', err)
        this.results = []
        this.found_docs = 0
      } finally {
        this.loading = false
      }
    },

    async updateSearch(newStart) {
      this.start = newStart
      console.log(`⏭️ Loading next page (start = ${newStart})`)
      await this.performSearch()
    },

    async filterByCluster(cluster = null) {
      this.start = 0
      this.selected_cluster = cluster
      console.log(`${cluster ? `Applying cluster filter: ${cluster.labels?.[0]}` : '🧹 Clearing cluster filter'}`)
      await this.performSearch()
    },
  },
})
