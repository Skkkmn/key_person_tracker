import request from './request'

export function listDepartments(params) {
  return request.get('/departments', { params })
}

export function getDepartment(id) {
  return request.get(`/departments/${id}`)
}

export function createDepartment(data) {
  return request.post('/departments', data)
}

export function updateDepartment(id, data) {
  return request.put(`/departments/${id}`, data)
}

export function deleteDepartment(id) {
  return request.delete(`/departments/${id}`)
}

export function getDepartmentTree() {
  return request.get('/departments/tree')
}
