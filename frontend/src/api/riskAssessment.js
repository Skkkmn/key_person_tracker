import request from './request'

export function calculateRisk(personId) {
  return request.get(`/risk-assessment/calculate/${personId}`)
}

export function applyRiskAssessment(personId, data) {
  return request.post(`/risk-assessment/apply/${personId}`, data)
}

export function getRiskHistory(personId) {
  return request.get(`/risk-assessment/history/${personId}`)
}

export function autoAssessAll() {
  return request.post('/risk-assessment/auto-all')
}
