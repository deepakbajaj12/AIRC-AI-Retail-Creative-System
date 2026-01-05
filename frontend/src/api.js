import axios from 'axios'

// Ensure API_URL does not end with a slash to avoid double slashes when appending paths
const rawUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
const API_URL = rawUrl.endsWith('/') ? rawUrl.slice(0, -1) : rawUrl

const api = axios.create({ baseURL: API_URL })

export const uploadAssets = async (files) => {
  const form = new FormData()
  for (const f of files) form.append('files', f)
  const { data } = await api.post('/uploads/assets', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.files
}

export const suggestLayouts = async (payload) => {
  const { data } = await api.post('/layout/suggest', payload)
  return data.candidates
}

export const checkCompliance = async (canvas) => {
  const { data } = await api.post('/compliance/check', { canvas })
  return data
}

export const serverAutofix = async (canvas) => {
  const { data } = await api.post('/compliance/autofix', { canvas })
  return data
}

export const exportImage = async (canvas, output_format='PNG') => {
  const { data } = await api.post('/export/image', { canvas, output_format })
  return { filePath: data.file_path, url: data.url, fileSizeBytes: data.file_size_bytes }
}

export const exportBatch = async (payload) => {
  const { data } = await api.post('/export/batch', payload)
  return data
}

export const listProjects = async () => {
  const { data } = await api.get('/projects')
  return data.projects
}

export const saveProject = async (id, canvas) => {
  const { data } = await api.post(`/projects/${id}`, canvas)
  return data
}

export const loadProject = async (id) => {
  const { data } = await api.get(`/projects/${id}`)
  return data
}

export const removeBackground = async (assetUrl) => {
  const { data } = await api.post('/uploads/remove_bg', null, { params: { url: assetUrl } })
  return data
}
