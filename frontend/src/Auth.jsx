import React, { useState, useEffect } from 'react'

export default function Auth({ onAuth }) {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('worker')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [activeStat, setActiveStat] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => setActiveStat(prev => (prev + 1) % 4), 3000)
    return () => clearInterval(interval)
  }, [])

  const handleAuth = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const endpoint = isLogin ? '/api/auth/login' : '/api/auth/signup'
      const body = isLogin ? { email, password } : { email, password, role }
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Authentication failed')
      localStorage.setItem('safeguard_token', data.token)
      localStorage.setItem('safeguard_user', JSON.stringify(data.user))
      onAuth(data.user)
    } catch (err) {
      setError(err.message || 'Authentication failed')
    }
    setLoading(false)
  }

  const stats = [
    { label: 'Reports Analyzed', value: '190+', icon: '\u{1F4CA}', color: 'var(--primary)' },
    { label: 'Classification Accuracy', value: '97.4%', icon: '\u{1F3AF}', color: 'var(--safe)' },
    { label: 'NLP Domain Terms', value: '230', icon: '\u{1F9E0}', color: 'var(--warning)' },
    { label: 'Facility Locations', value: '25', icon: '\u{1F4CD}', color: '#a78bfa' },
  ]

  const inputStyle = {
    width: '100%', padding: '14px 16px', borderRadius: 10, border: '1px solid var(--border)',
    background: 'rgba(0,0,0,0.3)', color: 'var(--text-main)', fontSize: '0.9rem',
    outline: 'none', fontFamily: 'inherit', boxSizing: 'border-box',
    transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-main)' }}>
      {/* Left: Branding */}
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center',
        alignItems: 'center', padding: '60px 40px', position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', top: '-20%', left: '-10%', width: 500, height: 500, borderRadius: '50%', background: 'radial-gradient(circle, rgba(24,198,217,0.08), transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: '-20%', right: '-10%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(239,68,68,0.05), transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ fontSize: 64, marginBottom: 16, filter: 'drop-shadow(0 0 20px rgba(24,198,217,0.3))' }}>{'\u{1F6E1}\uFE0F'}</div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text-main)', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 8 }}>SAFEGUARD AI</h1>
        <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', marginBottom: 40, textAlign: 'center', maxWidth: 400, lineHeight: 1.6 }}>Protecting Oil India's workers before accidents happen</p>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 16, padding: '24px 32px', width: '100%', maxWidth: 360, textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>{stats[activeStat].icon}</div>
          <div style={{ fontSize: '2rem', fontWeight: 800, color: stats[activeStat].color, transition: 'color 0.5s ease' }}>{stats[activeStat].value}</div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: 4 }}>{stats[activeStat].label}</div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginTop: 16 }}>
            {stats.map((_, i) => (
              <div key={i} style={{ width: 8, height: 8, borderRadius: 4, background: i === activeStat ? 'var(--primary)' : 'var(--border)', transition: 'all 0.3s ease' }} />
            ))}
          </div>
        </div>
        <div style={{ display: 'flex', gap: 8, marginTop: 32, flexWrap: 'wrap', justifyContent: 'center' }}>
          {['NLP Extraction', 'Risk Scoring', 'Knowledge Graph', 'AI Chatbot'].map(f => (
            <span key={f} style={{ padding: '6px 14px', borderRadius: 20, fontSize: '0.75rem', fontWeight: 600, background: 'rgba(24,198,217,0.1)', border: '1px solid rgba(24,198,217,0.3)', color: 'var(--primary)' }}>{f}</span>
          ))}
        </div>
      </div>

      {/* Right: Auth Form */}
      <div style={{ width: 480, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40, background: 'var(--bg-surface)', borderLeft: '1px solid var(--border)' }}>
        <div style={{ width: '100%', maxWidth: 360 }}>
          <div style={{ display: 'flex', marginBottom: 28, borderRadius: 10, overflow: 'hidden', border: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
            <button onClick={() => { setIsLogin(true); setError(''); }} style={{ flex: 1, padding: '12px 0', border: 'none', cursor: 'pointer', fontWeight: 700, fontSize: '0.9rem', background: isLogin ? 'var(--primary)' : 'transparent', color: isLogin ? '#000' : 'var(--text-muted)', transition: 'all 0.3s ease' }}>Sign In</button>
            <button onClick={() => { setIsLogin(false); setError(''); }} style={{ flex: 1, padding: '12px 0', border: 'none', cursor: 'pointer', fontWeight: 700, fontSize: '0.9rem', background: !isLogin ? 'var(--primary)' : 'transparent', color: !isLogin ? '#000' : 'var(--text-muted)', transition: 'all 0.3s ease' }}>Sign Up</button>
          </div>
          {error && (
            <div style={{ padding: '12px 16px', borderRadius: 10, background: 'rgba(239,68,68,0.1)', border: '1px solid var(--critical)', color: 'var(--critical)', fontSize: '0.8rem', marginBottom: 20 }}>{error}</div>
          )}
          <form onSubmit={handleAuth}>
            <div style={{ marginBottom: 18 }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, letterSpacing: 0.5 }}>EMAIL</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@oilindia.com" required style={inputStyle}
                onFocus={(e) => { e.target.style.borderColor = 'var(--primary)'; e.target.style.boxShadow = '0 0 0 3px rgba(24,198,217,0.15)'; }}
                onBlur={(e) => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none'; }}
              />
            </div>
            <div style={{ marginBottom: 18 }}>
              <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, letterSpacing: 0.5 }}>PASSWORD</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Minimum 6 characters" required minLength={6} style={inputStyle}
                onFocus={(e) => { e.target.style.borderColor = 'var(--primary)'; e.target.style.boxShadow = '0 0 0 3px rgba(24,198,217,0.15)'; }}
                onBlur={(e) => { e.target.style.borderColor = 'var(--border)'; e.target.style.boxShadow = 'none'; }}
              />
            </div>
            {!isLogin && (
              <div style={{ marginBottom: 24 }}>
                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8, fontWeight: 600, letterSpacing: 0.5 }}>ROLE</label>
                <select value={role} onChange={(e) => setRole(e.target.value)} style={{ ...inputStyle, cursor: 'pointer' }}>
                  <option value="worker">Field Worker</option>
                  <option value="safety_officer">Safety Officer</option>
                  <option value="admin">Administrator</option>
                </select>
              </div>
            )}
            {isLogin && <div style={{ marginBottom: 24 }} />}
            <button type="submit" disabled={loading}
              style={{ width: '100%', padding: '14px', borderRadius: 10, border: 'none', cursor: 'pointer', background: loading ? 'var(--text-muted)' : 'var(--primary)', color: '#000', fontWeight: 700, fontSize: '1rem', transition: 'all 0.3s ease', boxShadow: loading ? 'none' : '0 4px 15px rgba(24,198,217,0.3)' }}
              onMouseEnter={(e) => { if (!loading) e.target.style.transform = 'scale(1.02)'; }}
              onMouseLeave={(e) => { if (!loading) e.target.style.transform = 'scale(1)'; }}
            >
              {loading ? 'Please wait...' : (isLogin ? 'Sign In \u2192' : 'Create Account \u2192')}
            </button>
          </form>
          <div style={{ textAlign: 'center', marginTop: 28 }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Oil India Limited</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4, opacity: 0.6 }}>No external services. Runs entirely on your server.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
