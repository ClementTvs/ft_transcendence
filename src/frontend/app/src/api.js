const API = ''

function getHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
}

function getAuthHeader() {
  const token = localStorage.getItem('token')
  return token ? { 'Authorization': `Bearer ${token}` } : {}
}

// ── Auth ──

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
  if (!res.ok) 
    throw new Error("Nom d'utilisateur ou mot de passe incorrect")
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
      throw new Error(messages[0])
    } else {
      const msg = data.detail
      if (msg === 'Username already registered') throw new Error("Le nom d'utilisateur existe déjà")
      else if (msg === 'Email already registered') throw new Error('Cet email est déjà lié à un autre compte')
      throw new Error(msg)
    }
  }
  return data
}

// ── User / Profile ──

export async function getProfile() {
  const res = await fetch(`${API}/api/users/me`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Non autorisé')
  return res.json()
}

export async function updateProfile(data) {
  const res = await fetch(`${API}/api/users/me`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify(data)
  })
  if (!res.ok) throw new Error('Erreur mise à jour profil')
  return res.json()
}

export async function getUserStats(userId) {
  const res = await fetch(`${API}/api/users/${userId}/stats`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur stats')
  return res.json()
}

export async function getUsers(search = '') {
  const query = search ? `?search=${encodeURIComponent(search)}` : ''
  const res = await fetch(`${API}/api/users/${query}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur users')
  return res.json()
}


export async function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API}/api/users/me/avatar`, {
    method: 'POST',
    headers: getAuthHeader(),
    body: formData
  })
  if (!res.ok) throw new Error('Erreur upload avatar')
  return res.json()
}

export async function uploadBanner(file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API}/api/users/me/banner`, {
    method: 'POST',
    headers: getAuthHeader(),
    body: formData
  })
  if (!res.ok) throw new Error('Erreur upload bannière')
  return res.json()
}


export async function getPosts(skip = 0, limit = 50) {
  const res = await fetch(`${API}/api/posts/?skip=${skip}&limit=${limit}`, { headers: getHeaders() })
  return res.json()
}

export async function getFollowingPosts() {
  const res = await fetch(`${API}/api/posts/following`, { headers: getHeaders() })
  return res.json()
}

export async function getUserPosts(userId) {
  const res = await fetch(`${API}/api/posts/user/${userId}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur posts utilisateur')
  return res.json()
}

export async function createPost(content, imageFile = null) {
  // Avec image: multipart/form-data sur /api/posts/with-image
  if (imageFile) {
    const formData = new FormData()
    formData.append('content', content)
    formData.append('file', imageFile)
    const res = await fetch(`${API}/api/posts/with-image`, {
      method: 'POST',
      headers: getAuthHeader(), // pas de Content-Type: le navigateur le met avec le boundary
      body: formData
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || 'Erreur création post')
    }
    return res.json()
  }

  // Sans image: JSON sur /api/posts/
  const res = await fetch(`${API}/api/posts/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ content })
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Erreur création post')
  }
  return res.json()
}

export async function uploadPostImage(postId, file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${API}/api/posts/${postId}/image`, {
    method: 'POST',
    headers: getAuthHeader(),
    body: formData
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Erreur upload image')
  }
  return res.json()
}

export async function deletePostImage(postId) {
  const res = await fetch(`${API}/api/posts/${postId}/image`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Erreur suppression image')
  }
  return res.json()
}

export async function deletePost(postId) {
  const res = await fetch(`${API}/api/posts/${postId}`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error('Erreur suppression post')
}

export async function likePost(postId) {
  const res = await fetch(`${API}/api/posts/${postId}/like`, {
    method: 'POST',
    headers: getHeaders()
  })
  return res.json()
}

export async function unlikePost(postId) {
  const res = await fetch(`${API}/api/posts/${postId}/like`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok && res.status !== 204) throw new Error('Erreur unlike')
}


export async function getComments(postId) {
  const res = await fetch(`${API}/api/comments/post/${postId}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur commentaires')
  return res.json()
}

export async function createComment(postId, content) {
  const res = await fetch(`${API}/api/comments/`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ post_id: postId, content })
  })
  if (!res.ok) throw new Error('Erreur création commentaire')
  return res.json()
}


export async function followUser(userId) {
  const res = await fetch(`${API}/api/social/follow/${userId}`, {
    method: 'POST',
    headers: getHeaders()
  })
  return res.json()
}

export async function unfollowUser(userId) {
  const res = await fetch(`${API}/api/social/unfollow/${userId}`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok && res.status !== 204) throw new Error('Erreur unfollow')
}

export async function isFollowing(userId) {
  const res = await fetch(`${API}/api/social/is-following/${userId}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur check follow')
  return res.json()
}

export async function getFollowers(userId) {
  const res = await fetch(`${API}/api/social/followers/${userId}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur followers')
  return res.json()
}

export async function getFollowing(userId) {
  const res = await fetch(`${API}/api/social/following/${userId}`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur following')
  return res.json()
}

export async function getSuggestions() {
  const res = await fetch(`${API}/api/social/suggestions`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur suggestions')
  return res.json()
}


export async function getNotifications() {
  const res = await fetch(`${API}/api/notifications`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur notifications')
  return res.json()
}

export async function getUnreadCount() {
  const res = await fetch(`${API}/api/notifications/unread-count`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur unread count')
  return res.json()
}


export async function getConversations() {
  const res = await fetch(`${API}/api/messages/conversations`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur conversations')
  return res.json()
}

export async function getOrCreateConversation(userId) {
  const res = await fetch(`${API}/api/messages/conversations/${userId}`, {
    method: 'POST',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error('Erreur création conversation')
  return res.json()
}

export async function getMessages(convId, skip = 0, limit = 50) {
  const res = await fetch(`${API}/api/messages/conversations/${convId}/messages?skip=${skip}&limit=${limit}`, {
    headers: getHeaders()
  })
  if (!res.ok) throw new Error('Erreur messages')
  return res.json()
}

export async function markConversationRead(convId) {
  const res = await fetch(`${API}/api/messages/conversations/${convId}/read`, {
    method: 'PUT',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error('Erreur mark read')
  return res.json()
}

export async function changePassword(current_password, new_password) {
  const res = await fetch(`${API}/api/users/me/password`, {
    method: 'PUT',
    headers: getHeaders(),
    body: JSON.stringify({
      current_password,
      new_password
    })
  })
  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || 'Password change error')
  }
  return res.json()
}

export async function deleteAccount() {
  const res = await fetch(`${API}/api/users/me`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok) {
    throw new Error('Account deletion error')
  }
  return true
}

export async function resetPassword(token, newPassword) {
  const res = await fetch(`${API}/api/auth/reset-password`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ token, new_password: newPassword })
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail || 'Lien invalide ou expiré')
  }
  return res.json()
}

export async function forgotPassword(email) 
{ 
  const res = await fetch(`${API}/api/auth/forgot-password`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify({ email })
  })
  if (!res.ok) {
    throw new Error('Error requesting password reset') 
  } 
  return await res.json() 
}

export async function blockUser(userId) {
  const res = await fetch(`${API}/api/social/block/${userId}`, {
    method: 'POST',
    headers: getHeaders()
  })
  if (!res.ok) throw new Error('Erreur lors du blocage')
  return res.json()
}

export async function unblockUser(userId) {
  const res = await fetch(`${API}/api/social/unblock/${userId}`, {
    method: 'DELETE',
    headers: getHeaders()
  })
  if (!res.ok && res.status !== 204) throw new Error('Erreur lors du déblocage')
  return true
}

export async function getBlockedUsers() {
  const res = await fetch(`${API}/api/social/blocked`, { headers: getHeaders() })
  if (!res.ok) throw new Error('Erreur récupération bloqués')
  return res.json()
}

export async function isBlocked(userId) {
  const blocked = await getBlockedUsers()
  return blocked.some(u => u.id === userId)
}