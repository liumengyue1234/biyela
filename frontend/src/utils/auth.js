/**
 * Token 管理工具
 */

const TOKEN_KEY = 'token'
const USER_INFO_KEY = 'userInfo'
const ROLES_KEY = 'roles'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function getUserInfo() {
  const info = localStorage.getItem(USER_INFO_KEY)
  return info ? JSON.parse(info) : {}
}

export function setUserInfo(info) {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(info))
}

export function removeUserInfo() {
  localStorage.removeItem(USER_INFO_KEY)
}

export function getRoles() {
  const roles = localStorage.getItem(ROLES_KEY)
  return roles ? JSON.parse(roles) : []
}

export function setRoles(roles) {
  localStorage.setItem(ROLES_KEY, JSON.stringify(roles))
}

export function removeRoles() {
  localStorage.removeItem(ROLES_KEY)
}

export function clearAuth() {
  removeToken()
  removeUserInfo()
  removeRoles()
}

export function isAuthenticated() {
  return !!getToken()
}

export function isAdmin() {
  return getRoles().includes('admin')
}
