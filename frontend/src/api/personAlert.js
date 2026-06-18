import request from './request'

export function listAlerts(params) {
  return request.get('/alerts', { params })
}

export function getAlertStats() {
  return request.get('/alerts/stats')
}

export function getAlert(id) {
  return request.get(`/alerts/${id}`)
}

export function createAlert(data) {
  return request.post('/alerts', data)
}

export function updateAlert(id, data) {
  return request.put(`/alerts/${id}`, data)
}

export function deleteAlert(id) {
  return request.delete(`/alerts/${id}`)
}

export function handleAlert(id, data) {
  return request.put(`/alerts/${id}/handle`, data)
}
