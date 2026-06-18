import request from './request'

export function listCases(params) {
  return request.get('/cases', { params })
}

export function getCase(id) {
  return request.get(`/cases/${id}`)
}

export function createCase(data) {
  return request.post('/cases', data)
}

export function updateCase(id, data) {
  return request.put(`/cases/${id}`, data)
}

export function deleteCase(id) {
  return request.delete(`/cases/${id}`)
}
