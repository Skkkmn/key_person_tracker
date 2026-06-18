import request from './request'

export function listTracks(params) {
  return request.get('/tracks', { params })
}

export function getTrack(id) {
  return request.get(`/tracks/${id}`)
}

export function createTrack(data) {
  return request.post('/tracks', data)
}

export function updateTrack(id, data) {
  return request.put(`/tracks/${id}`, data)
}

export function deleteTrack(id) {
  return request.delete(`/tracks/${id}`)
}

export function getPersonTracks(personId) {
  return request.get('/tracks', { params: { person_id: personId } })
}

export function getGeoDistribution(params) {
  return request.get('/tracks/geo-distribution', { params })
}
