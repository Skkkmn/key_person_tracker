import request from './request'

export function listLogs(params) {
  return request.get('/logs', { params })
}
