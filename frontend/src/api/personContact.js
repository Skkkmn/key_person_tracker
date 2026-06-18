import request from './request'

export function listContacts(params) {
  return request.get('/contacts', { params })
}

export function getContact(id) {
  return request.get(`/contacts/${id}`)
}

export function createContact(data) {
  return request.post('/contacts', data)
}

export function updateContact(id, data) {
  return request.put(`/contacts/${id}`, data)
}

export function deleteContact(id) {
  return request.delete(`/contacts/${id}`)
}
