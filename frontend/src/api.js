import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

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

export const exportImage = async (canvas, output_format='PNG') => {
  const { data } = await api.post('/export/image', { canvas, output_format })
  return { filePath: data.file_path, url: data.url }
}
