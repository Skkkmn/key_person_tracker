import request from './request'

export function listTags(params) {
  return request.get('/tags', { params })
}

export function createTag(data) {
  return request.post('/tags', data)
}

export function updateTag(id, data) {
  return request.put(`/tags/${id}`, data)
}

export function deleteTag(id) {
  return request.delete(`/tags/${id}`)
}

export function getPersonTags(personId) {
  return request.get(`/tags/person/${personId}`)
}

export function setPersonTags(personId, tagIds) {
  return request.post(`/tags/person/${personId}`, { tag_ids: tagIds })
}
