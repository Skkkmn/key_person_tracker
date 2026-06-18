import request from './request'

export function exportPersons() {
  const token = localStorage.getItem('token')
  window.open(`/api/import-export/export/persons?token=${token}`, '_blank')
}

export function getPersonArchive(personId) {
  return request.get(`/import-export/archive/${personId}`)
}
