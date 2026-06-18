import request from './request'

export function listVisitTasks(params) {
  return request.get('/visit-tasks', { params })
}

export function getVisitTask(id) {
  return request.get(`/visit-tasks/${id}`)
}

export function createVisitTask(data) {
  return request.post('/visit-tasks', data)
}

export function updateVisitTask(id, data) {
  return request.put(`/visit-tasks/${id}`, data)
}

export function deleteVisitTask(id) {
  return request.delete(`/visit-tasks/${id}`)
}

export function getVisitTaskStats() {
  return request.get('/visit-tasks/stats')
}

export function autoGenerateTasks() {
  return request.post('/visit-tasks/auto-generate')
}
