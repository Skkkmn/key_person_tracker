import request from './request'

export function listLostContactTracks(params) {
  return request.get('/lost-contacts', { params })
}

export function getLostContactTrack(id) {
  return request.get(`/lost-contacts/${id}`)
}

export function createLostContactTrack(data) {
  return request.post('/lost-contacts', data)
}

export function updateLostContactTrack(id, data) {
  return request.put(`/lost-contacts/${id}`, data)
}

export function deleteLostContactTrack(id) {
  return request.delete(`/lost-contacts/${id}`)
}
