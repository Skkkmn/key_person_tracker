import axios from 'axios'
import request from './request'

export function login(data) {
  return request.post('/auth/login', data)
}

export function getUserInfo() {
  return request.get('/auth/info')
}

export function changePassword(data) {
  return request.put('/auth/password', data)
}

export async function getCaptcha() {
  const res = await axios.get('/api/auth/captcha', { responseType: 'blob' })
  return {
    image: res.data,
    token: res.headers['x-captcha-token'],
  }
}
