import request from './request'

export function listCrossRegionTracks(params) {
  return request.get('/cross-region', { params })
}

export function getCrossRegionTrack(id) {
  return request.get(`/cross-region/${id}`)
}

export function createCrossRegionTrack(data) {
  return request.post('/cross-region', data)
}

export function updateCrossRegionTrack(id, data) {
  return request.put(`/cross-region/${id}`, data)
}

export function deleteCrossRegionTrack(id) {
  return request.delete(`/cross-region/${id}`)
}

export function pushCrossRegionNotification(id) {
  return request.post(`/cross-region/${id}/push`)
}

export function getCrossRegionStats() {
  return request.get('/cross-region/stats')
}
