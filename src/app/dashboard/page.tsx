'use client'
import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/context/AuthContext'
import { api } from '@/lib/api'

const STYLES = [
  { id: 'cinematic', label: 'Cinematic', emoji: '🎥', desc: 'Epic film quality' },
  { id: 'anime', label: 'Anime', emoji: '⛩️', desc: 'Vibrant anime style' },
  { id: 'neon', label: 'Neon Cyberpunk', emoji: '🌆', desc: 'Glowing city nights' },
  { id: 'abstract', label: 'Abstract', emoji: '🌀', desc: 'Psychedelic visuals' },
  { id: 'nature', label: 'Nature', emoji: '🌿', desc: 'Sweeping landscapes' },
  { id: 'concert', label: 'Concert', emoji: '🎸', desc: 'Live stage energy' },
]

type Project = {
  id: number; title: string; style: string; status: string
  audio_url: string | null; video_url: string | null
  bpm: number | null; duration: number | null; created_at: string
}

export default function Dashboard() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [projects, setProjects] = useState<Project[]>([])
  const [title, setTitle] = useState('')
  const [style, setStyle] = useState('cinematic')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading])

  useEffect(() => {
    if (user) fetchProjects()
  }, [user])

  // Poll for in-progress projects
  useEffect(() => {
    const hasActive = projects.some(p => p.status === 'pending' || p.status === 'generating')
    if (!hasActive) return
    const interval = setInterval(fetchProjects, 5000)
    return () => clearInterval(interval)
  }, [projects])

  const fetchProjects = async () => {
    try { setProjects(await api.listProjects()) } catch {}
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return
    setUploading(true); setError('')
    try {
      await api.createProject(title, style, file)
      setTitle(''); setFile(null); if (fileRef.current) fileRef.current.value = ''
      await fetchProjects()
    } catch (err: unknown) {
      const e = err as { detail?: string }
      setError(e?.detail || 'Upload failed. Please try again.')
    }
    finally { setUploading(false) }
  }

  const statusColor = (s: string) => {
    if (s === 'completed') return 'bg-green-900 text-green-300'
    if (s === 'generating') return 'bg-blue-900 text-blue-300'
    if (s === 'failed') return 'bg-red-900 text-red-300'
    return 'bg-yellow-900 text-yellow-300'
  }

  const statusLabel = (s: string) => {
    if (s === 'pending') return '⏳ Queued'
    if (s === 'generating') return '🎬 Generating...'
    if (s === 'completed') return '✅ Ready'
    if (s === 'failed') return '❌ Failed'
    return s
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎬</span>
            <span className="font-bold text-lg bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">MusicVideo AI</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">{user?.email}</span>
            <button onClick={() => { logout(); router.push('/login') }}
              className="text-sm border border-gray-700 px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors">
              Sign out
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-8">
        {/* Create new video */}
        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800 mb-8">
          <h2 className="text-xl font-bold mb-1">🎵 Create a Music Video</h2>
          <p className="text-gray-400 text-sm mb-6">Upload your track and our AI will generate a stunning music video</p>

          {error && <p className="text-red-400 text-sm mb-4 bg-red-900/20 p-3 rounded-lg">{error}</p>}

          <form onSubmit={submit} className="space-y-6">
            <input type="text" placeholder="Song title (e.g. Midnight Waves)" value={title} onChange={e => setTitle(e.target.value)}
              className="w-full bg-gray-800 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-purple-500 border border-gray-700" required />

            {/* Style picker */}
            <div>
              <p className="text-sm text-gray-400 mb-3">Choose a visual style</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {STYLES.map(s => (
                  <button key={s.id} type="button" onClick={() => setStyle(s.id)}
                    className={`p-4 rounded-xl border text-left transition-all ${style === s.id ? 'border-purple-500 bg-purple-900/30' : 'border-gray-700 hover:border-gray-600 bg-gray-800'}`}>
                    <div className="text-2xl mb-1">{s.emoji}</div>
                    <div className="font-semibold text-sm">{s.label}</div>
                    <div className="text-xs text-gray-400">{s.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* File upload */}
            <div onClick={() => fileRef.current?.click()}
              className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center cursor-pointer hover:border-purple-500 transition-colors">
              <input ref={fileRef} type="file" accept=".mp3,.wav,.flac,.m4a,.aac" className="hidden"
                onChange={e => setFile(e.target.files?.[0] || null)} />
              {file ? (
                <div>
                  <div className="text-3xl mb-2">🎵</div>
                  <p className="font-semibold">{file.name}</p>
                  <p className="text-xs text-gray-400 mt-1">{(file.size / 1024 / 1024).toFixed(1)} MB</p>
                </div>
              ) : (
                <div>
                  <div className="text-3xl mb-2">🎵</div>
                  <p className="font-semibold">Drop your audio file here</p>
                  <p className="text-xs text-gray-400 mt-1">MP3, WAV, FLAC, M4A supported</p>
                </div>
              )}
            </div>

            <button type="submit" disabled={uploading || !file || !title}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 py-4 rounded-xl font-bold text-lg disabled:opacity-50 transition-all">
              {uploading ? '✨ Starting AI Generation...' : '🚀 Generate Music Video'}
            </button>
          </form>
        </div>

        {/* Projects list */}
        <div>
          <h2 className="text-xl font-bold mb-4">Your Videos</h2>
          {projects.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <div className="text-5xl mb-4">🎬</div>
              <p>No videos yet. Upload your first track above!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {projects.map(p => (
                <div key={p.id} className="bg-gray-900 rounded-2xl p-5 border border-gray-800">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-semibold text-lg">{p.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {STYLES.find(s => s.id === p.style)?.emoji} {STYLES.find(s => s.id === p.style)?.label}
                        {p.bpm && ` · ${Math.round(p.bpm)} BPM`}
                        {p.duration && ` · ${Math.round(p.duration)}s`}
                      </p>
                    </div>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${statusColor(p.status)}`}>
                      {statusLabel(p.status)}
                    </span>
                  </div>

                  {(p.status === 'pending' || p.status === 'generating') && (
                    <div className="mt-4">
                      <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-purple-600 to-pink-600 rounded-full animate-pulse" style={{ width: p.status === 'generating' ? '65%' : '15%' }} />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {p.status === 'pending' ? 'Analyzing audio...' : 'AI generating your video (2–5 mins)...'}
                      </p>
                    </div>
                  )}

                  {p.status === 'completed' && p.video_url && (
                    <div className="mt-4">
                      <video src={p.video_url} controls className="w-full rounded-xl mt-2 max-h-64 bg-black" />
                      <a href={p.video_url} download className="inline-block mt-2 text-sm text-purple-400 hover:underline">
                        ⬇️ Download video
                      </a>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
