import request from './request'

export function listPersons(params) {
  return request.get('/persons', { params })
}

export function getAllPersons() {
  return request.get('/persons/all')
}

export function getPerson(id) {
  return request.get(`/persons/${id}`)
}

export function createPerson(data) {
  return request.post('/persons', data)
}

export function updatePerson(id, data) {
  return request.put(`/persons/${id}`, data)
}

export function deletePerson(id) {
  return request.delete(`/persons/${id}`)
}

export function archivePerson(id, reason) {
  return request.put(`/persons/${id}/archive`, { reason })
}

export function markLost(id, lostInfo) {
  return request.put(`/persons/${id}/lost`, { lost_info: lostInfo })
}

export function updatePersonStatus(id, data) {
  return request.put(`/persons/${id}/status`, data)
}

export function getPersonStats() {
  return request.get('/persons/stats')
}
