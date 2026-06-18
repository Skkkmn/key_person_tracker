import request from './request'

export function listVisitRecords(params) {
  return request.get('/visit-records', { params })
}

export function getVisitRecord(id) {
  return request.get(`/visit-records/${id}`)
}

export function createVisitRecord(data) {
  return request.post('/visit-records', data)
}

export function updateVisitRecord(id, data) {
  return request.put(`/visit-records/${id}`, data)
}

export function deleteVisitRecord(id) {
  return request.delete(`/visit-records/${id}`)
}
