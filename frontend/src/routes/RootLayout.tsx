import { Outlet, Link, useLocation } from 'react-router-dom'
import DarkModeToggle from '../shared/DarkModeToggle'

export default function RootLayout() {
  const location = useLocation()
  const isActive = (to: string) => (location.pathname === to || (to !== '/' && location.pathname.startsWith(to)))
  return (
    <div className="min-h-full flex flex-col bg-neutral-50 text-slate-800 dark:bg-slate-950 dark:text-slate-100">
      <header className="fixed top-0 inset-x-0 z-50 bg-white/80 dark:bg-slate-900/80 backdrop-blur border-b border-slate-200 dark:border-slate-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/" className="font-semibold">SOP Generator</Link>
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className={`text-sm px-3 py-1 rounded transition-colors ${isActive('/') ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'opacity-80 hover:opacity-100 border border-transparent hover:border-slate-300 dark:hover:border-slate-700'}`}
            >
              Home
            </Link>
            <Link
              to="/docs"
              className={`text-sm px-3 py-1 rounded transition-colors ${isActive('/docs') ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900' : 'opacity-80 hover:opacity-100 border border-transparent hover:border-slate-300 dark:hover:border-slate-700'}`}
            >
              API Docs
            </Link>
            <DarkModeToggle />
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 pt-16 pb-6">
        <Outlet />
      </main>
      <footer className="mt-10 border-t border-gray-200 dark:border-slate-700 bg-white/50 dark:bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-sm text-gray-600 dark:text-slate-400 flex items-center justify-between">
          <div className="text-left">
            <p>© 2025 Developer Viewpoint. All rights reserved.</p>
            <p className="mt-0.5">Free source code available on GitHub (MIT Licensed).</p>
          </div>
          <p className="text-right">Developed by <span className="font-semibold text-gray-800 dark:text-slate-200">Anshul</span>.</p>
        </div>
      </footer>
    </div>
  )
}
