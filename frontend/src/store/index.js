import { defineStore } from 'pinia'

const ROLE_LEVELS = { viewer: 1, operator: 2, dept_admin: 3, super_admin: 4 }

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => (ROLE_LEVELS[state.user?.role] || 0) >= 3,
    isSuperAdmin: (state) => state.user?.role === 'super_admin',
    roleLevel: (state) => ROLE_LEVELS[state.user?.role] || 0,
    username: (state) => state.user?.real_name || '',
  },
  actions: {
    setToken(token) {
      this.token = token
      localStorage.setItem('token', token)
    },
    setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },
  },
})
