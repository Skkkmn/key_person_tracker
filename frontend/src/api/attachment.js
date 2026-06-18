import request from './request'

export function uploadFile(entityType, entityId, file) {
  const form = new FormData()
  form.append('file', file)
  form.append('entity_type', entityType)
  form.append('entity_id', entityId)
  return request.post('/attachments/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function listAttachments(params) {
  return request.get('/attachments/list', { params })
}

export function deleteAttachment(id) {
  return request.delete(`/attachments/${id}`)
}
