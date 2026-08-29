import React, { useState } from 'react'

export default function Auth({ onAuth }) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('worker')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleAuth = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup'
      const body = isLogin
        ? { email, password }
        : { email, password, role }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Authentication failed')

      // Store token in localStorage
      localStorage.setItem('safeguard_token', data.token)
      localStorage.setItem('safeguard_user', JSON.stringify(data.user))
      onAuth(data.user)
    } catch (err) {
      setError(err.message || 'Authentication failed')
    }
    setLoading(false)
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'var(--bg-main)',
      padding: 20,
    }}>
      <div style={{
        width: '100%',
        maxWidth: 420,
        background: 'var(--bg-surface)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: 40,
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
      }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>🛡️</div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: 1 }}>
            SAFEGUARD AI
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>
            Industrial Safety Intelligence Platform
          </p>
        </div>

        {/* Tab Toggle */}
        <div style={{ display: 'flex', marginBottom: 24, borderRadius: 8, overflow: 'hidden', border: '1px solid var(--border)' }}>
          <button
            onClick={() => { setIsLogin(true); setError(''); }}
            style={{
              flex: 1, padding: '10px 0', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem',
              background: isLogin ? 'var(--primary)' : 'transparent',
              color: isLogin ? '#000' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            Sign In
          </button>
          <button
            onClick={() => { setIsLogin(false); setError(''); }}
            style={{
              flex: 1, padding: '10px 0', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '0.9rem',
              background: !isLogin ? 'var(--primary)' : 'transparent',
              color: !isLogin ? '#000' : 'var(--text-muted)',
              transition: 'all 0.2s',
            }}
          >
            Sign Up
          </button>
        </div>

        {/* Error */}
        {error && (
          <div style={{ padding: '10px 14px', borderRadius: 8, background: 'rgba(239,68,68,0.1)', border: '1px solid var(--critical)', color: 'var(--critical)', fontSize: '0.8rem', marginBottom: 16 }}>
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleAuth}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@oilindia.com"
              required
              style={{
                width: '100%', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'rgba(0,0,0,0.2)', color: 'var(--text-main)', fontSize: '0.9rem',
                outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box',
              }}
            />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              minLength={6}
              style={{
                width: '100%', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)',
                background: 'rgba(0,0,0,0.2)', color: 'var(--text-main)', fontSize: '0.9rem',
                outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box',
              }}
            />
          </div>

          {/* Role selector (signup only) */}
          {!isLogin && (
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 6, fontWeight: 600 }}>
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                style={{
                  width: '100%', padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)',
                  background: 'rgba(0,0,0,0.2)', color: 'var(--text-main)', fontSize: '0.9rem',
                  outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box', cursor: 'pointer',
                }}
              >
                <option value="worker">👷 Field Worker</option>
                <option value="safety_officer">🛡️ Safety Officer</option>
                <option value="admin">⚙️ Administrator</option>
              </select>
            </div>
          )}

          {isLogin && <div style={{ marginBottom: 24 }} />}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '12px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: 'var(--primary)', color: '#000', fontWeight: 700, fontSize: '0.95rem',
              opacity: loading ? 0.6 : 1, transition: 'all 0.2s',
            }}
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Create Account')}
          </button>
        </form>

        {/* Footer */}
        <div style={{ textAlign: 'center', marginTop: 24, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Oil India Limited — Duliajan Facility
        </div>
        <div style={{ textAlign: 'center', marginTop: 8, fontSize: '0.65rem', color: 'var(--text-muted)', opacity: 0.6 }}>
          No external services • Runs entirely on your server
        </div>
      </div>
    </div>
  )
}
