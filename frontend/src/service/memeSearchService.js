import axios from 'axios'

const SOLR_BASE_PATH = import.meta.env.VITE_SOLR_PATH
const SOLR_URL = `${SOLR_BASE_PATH}/solr/memes_collection/select`

export async function fetchClusters() {
  const params = {
    q: '*:*',
    rows: 100000,
    clustering: true,
    'clustering.engine': 'lingo',
    wt: 'json',
  }

  try {
    const response = await axios.get(SOLR_URL, { params })
    console.log('✔️ Clusters fetched successfully')
    return response.data.clusters || []
  } catch (error) {
    console.error('❌ Failed to fetch clusters:', error)
    return []
  }
}

export async function searchForAMeme(title, media_type, tags, start, cluster_docs) {
  const filters = []

  if (cluster_docs && cluster_docs.length > 0) filters.push(`{!terms f=id}${cluster_docs.join(',')}`)
  if (tags) filters.push(`tags:${tags}`)
  if (media_type) filters.push(`media_type:${media_type}`)

  const query_body = {
    query: title ? `title:${title}` : '*:*',
    filter: filters,
    offset: start,
    limit: 12,
  }

  try {
    const response = await axios.post(SOLR_URL, query_body)
    console.log('✔️ Meme search completed successfully')
    return response.data || []
  } catch (error) {
    console.error('❌ Meme search failed:', error)
    return { response: { docs: [] } }
  }
}
