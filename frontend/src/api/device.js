import request from './request'

export function listDevices(params) {
  return request.get('/devices', { params })
}

export function getDevice(id) {
  return request.get(`/devices/${id}`)
}

export function bindDevice(data) {
  return request.post('/devices/bind', data)
}

export function unbindDevice(id) {
  return request.post(`/devices/${id}/unbind`)
}

export function getPersonDeviceLocation(personId) {
  return request.get(`/devices/person/${personId}/location`)
}
