const API = 'http://localhost:8000'

function getHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

export async function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const res = await fetch(`${API}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail)
  localStorage.setItem('token', data.access_token)
  return data
}

export async function register(username, email, password) {
  const res = await fetch(`${API}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password })
  })
  const data = await res.json()
  if (!res.ok) {
    if (Array.isArray(data.detail)) {
      const messages = data.detail.map(e => {
        if (e.msg.includes('at least 6 characters')) return 'Le mot de passe doit faire au moins 6 caractères'
        else if (e.msg.includes('value is not a valid email address: An email address must have an @-sign.')) return 'Adresse email invalide'
        return e.msg
      })
      throw new Error(messages[0]);
    } else {
        const msg = data.detail
        if (msg === 'Username already registered') throw new Error("Le nom d'utilisateur existe déjà")
        else if (msg === 'Email already registered') throw new Error('Cet email est déjà lié à un autre compte')
        throw new Error(msg)
    }
  }
  return data
}

export async function getProfile() {
  const res = await fetch(`${API}/api/users/me`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function getPosts() {
  const res = await fetch(`${API}/api/posts`, { headers: getHeaders() })
  return res.json()
}

export async function createPost(content) {
  const res = await fetch(`${API}/api/posts`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ content })
  })
  return res.json()
}

export async function likePost(postId) {
  const res = await fetch(`${API}/api/posts/${postId}/like`, {
    method: 'POST',
    headers: getHeaders()
  })
  return res.json()
}

export async function followUser(userId) {
  const res = await fetch(`${API}/api/social/follow/${userId}`, {
    method: 'POST',
    headers: getHeaders()
  })
  return res.json()
}