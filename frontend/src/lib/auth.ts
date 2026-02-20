import api from './api'
import type { User, LoginCredentials, RegisterData } from '@/types'

export async function register(data: RegisterData): Promise<User> {
  const response = await api.post('/auth/register', data)
  return response.data
}

export async function login(credentials: LoginCredentials): Promise<void> {
  await api.post('/auth/login', credentials)
}

export async function logout(): Promise<void> {
  await api.post('/auth/logout')
}

export async function getMe(): Promise<User> {
  const response = await api.get('/auth/me')
  return response.data
}
