import Link from 'next/link';
import { ArrowRight, Play, Activity, Zap, Shield, Globe, Layers, UploadCloud, ChevronRight, BarChart3, Users, Clock } from 'lucide-react';
import { SignedIn, SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 font-sans selection:bg-orange-500/30 selection:text-orange-200 overflow-x-hidden">
      
      {/* Background Gradients */}
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] right-[-20%] w-[60%] h-[60%] bg-orange-600/10 blur-[150px] rounded-full" />
        <div className="absolute bottom-[-20%] left-[20%] w-[40%] h-[40%] bg-purple-600/15 blur-[120px] rounded-full" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 flex items-center justify-between px-6 py-6 md:px-12 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center shadow-lg shadow-orange-500/20 border border-orange-400/20">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2c.46-1.7.46-5.33.46-5.33a29 29 0 0 0-.46-5.33z" />
              <polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02" fill="white" />
            </svg>
          </div>
          <span className="text-xl font-black tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-neutral-400">
            Unified Marketing
          </span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-neutral-400">
          <a href="#features" className="hover:text-white transition-colors">Platform</a>
          <a href="#orchestration" className="hover:text-white transition-colors">Orchestration</a>
          <a href="#metrics" className="hover:text-white transition-colors">Metrics</a>
        </div>
        <div>
          <SignedOut>
            <div className="flex items-center gap-4">
              <SignInButton mode="modal">
                <button className="text-sm font-semibold text-neutral-400 hover:text-white transition-colors">Sign In</button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="group px-5 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm font-semibold text-white transition-all flex items-center gap-2 backdrop-blur-md">
                  Get Started
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </SignUpButton>
            </div>
          </SignedOut>
          <SignedIn>
            <Link 
              href="/dashboard"
              className="group px-5 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-sm font-semibold text-white transition-all flex items-center gap-2 backdrop-blur-md"
            >
              Launch Console
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </SignedIn>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 pt-20 pb-32 px-6 md:px-12 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="animate-in fade-in slide-in-from-bottom-8 duration-1000 flex flex-col items-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-bold uppercase tracking-widest mb-8 shadow-[0_0_30px_rgba(249,115,22,0.15)]">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
            </span>
            System v2.4 Online
          </div>
          
          <h1 className="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter leading-[1.1] mb-8 text-transparent bg-clip-text bg-gradient-to-b from-white via-white to-neutral-500 max-w-5xl">
            Automate Your <br className="hidden md:block" />
            <span className="relative">
              Audience Reach
              <div className="absolute -bottom-2 left-0 w-full h-[6px] bg-gradient-to-r from-orange-500 to-transparent rounded-full opacity-50 blur-sm"></div>
              <div className="absolute -bottom-2 left-0 w-full h-[2px] bg-gradient-to-r from-orange-500 to-transparent rounded-full"></div>
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-neutral-400 max-w-2xl mb-12 leading-relaxed font-medium">
            Deploy content across YouTube, Instagram, and Facebook seamlessly. Monitor live customer data, orchestrate rendering nodes, and command your entire marketing ecosystem from a single, robust pane of glass.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <SignedOut>
              <SignUpButton mode="modal">
                <button className="group relative px-8 py-4 bg-orange-600 hover:bg-orange-500 rounded-2xl text-white font-bold text-lg transition-all shadow-[0_0_40px_rgba(234,88,12,0.3)] hover:shadow-[0_0_60px_rgba(234,88,12,0.5)] hover:-translate-y-1 flex items-center gap-3 overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-[150%] animate-[shimmer_2s_infinite]"></div>
                  Start Automating
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link 
                href="/dashboard"
                className="group relative px-8 py-4 bg-orange-600 hover:bg-orange-500 rounded-2xl text-white font-bold text-lg transition-all shadow-[0_0_40px_rgba(234,88,12,0.3)] hover:shadow-[0_0_60px_rgba(234,88,12,0.5)] hover:-translate-y-1 flex items-center gap-3 overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-[150%] animate-[shimmer_2s_infinite]"></div>
                Enter Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </SignedIn>
            <a 
              href="#features"
              className="px-8 py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-white font-bold text-lg transition-all flex items-center gap-3 backdrop-blur-md"
            >
              System Capabilities
            </a>
          </div>
        </div>

        {/* Hero Visual Output (Mockup replacement) */}
        <div className="mt-24 w-full relative animate-in fade-in slide-in-from-bottom-12 duration-1000 delay-300">
          <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-transparent to-transparent z-10"></div>
          <div className="relative rounded-3xl border border-white/10 bg-neutral-900/50 backdrop-blur-2xl p-2 md:p-4 shadow-2xl overflow-hidden aspect-[16/9] max-h-[600px] flex flex-col">
            {/* Fake Browser Header */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
                <div className="w-3 h-3 rounded-full bg-green-500/80"></div>
              </div>
              <div className="mx-auto px-12 py-1 bg-black/40 rounded-md text-[10px] text-neutral-500 font-mono flex items-center gap-2">
                <Shield className="w-3 h-3 text-green-500" />
                https://marketing-os.internal/dashboard
              </div>
            </div>
            {/* Fake App Body */}
            <div className="flex-1 bg-neutral-950 rounded-b-xl flex p-4 gap-4 overflow-hidden relative">
              {/* Sidebar rough mock */}
              <div className="w-48 bg-neutral-900/50 rounded-lg p-4 flex flex-col gap-3">
                <div className="h-4 w-24 bg-white/10 rounded mb-4"></div>
                <div className="h-8 w-full bg-orange-500/20 rounded border border-orange-500/30"></div>
                <div className="h-8 w-full bg-white/5 rounded"></div>
                <div className="h-8 w-full bg-white/5 rounded"></div>
              </div>
              {/* Main area rough mock */}
              <div className="flex-1 flex flex-col gap-4">
                <div className="flex gap-4">
                  <div className="flex-1 h-24 bg-gradient-to-br from-blue-900/30 to-blue-900/10 rounded-xl border border-blue-500/20 p-4">
                    <div className="w-32 h-3 mx-auto bg-blue-400/30 rounded mt-8"></div>
                  </div>
                  <div className="flex-1 h-24 bg-gradient-to-br from-orange-900/30 to-orange-900/10 rounded-xl border border-orange-500/20 p-4">
                    <div className="w-32 h-3 mx-auto bg-orange-400/30 rounded mt-8"></div>
                  </div>
                </div>
                <div className="flex-1 flex gap-4">
                   <div className="flex-2 w-2/3 bg-neutral-900/50 rounded-xl border border-white/5 p-4">
                      {/* Fake Chart */}
                      <div className="w-full h-full flex items-end gap-2 pb-2">
                        {[40, 70, 45, 90, 65, 80, 100].map((h, i) => (
                           <div key={i} className="flex-1 bg-orange-500/40 rounded-t-sm" style={{ height: `${h}%` }}></div>
                        ))}
                      </div>
                   </div>
                   <div className="flex-1 bg-neutral-900/50 rounded-xl border border-white/5 relative overflow-hidden">
                     {/* Radar sweep effect */}
                     <div className="absolute inset-0 bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(59,130,246,0.3)_360deg)] animate-[spin_3s_linear_infinite] rounded-full scale-150 transform-gpu opacity-50"></div>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Bento Grid Features */}
      <section id="features" className="relative z-10 py-32 px-6 md:px-12 bg-neutral-950/50 border-t border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="mb-16">
            <h2 className="text-3xl md:text-5xl font-black tracking-tighter mb-4">Enterprise-grade Orchestration.</h2>
            <p className="text-neutral-400 text-lg md:text-xl max-w-2xl">A unified infrastructure designed to bridge local media processing with global social network distribution.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[250px]">
            {/* Feature 1: Omnichannel */}
            <div className="md:col-span-2 relative group overflow-hidden rounded-3xl bg-neutral-900/50 border border-white/10 p-8 flex flex-col justify-end backdrop-blur-md transition-colors hover:bg-neutral-900/80">
              <div className="absolute top-0 right-0 p-8 opacity-20 group-hover:opacity-40 transition-opacity">
                <Globe className="w-48 h-48 text-blue-500" />
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center mb-6 border border-blue-500/30 text-blue-400">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold mb-2 text-white">Omnichannel Distribution</h3>
                <p className="text-neutral-400 max-w-md">Push HD Video and Reels simultaneously to YouTube, Instagram, and Facebook with automatic format compliance.</p>
              </div>
            </div>

            {/* Feature 2: Ngrok Pipeline */}
            <div className="relative group overflow-hidden rounded-3xl bg-neutral-900/50 border border-white/10 p-8 flex flex-col justify-end backdrop-blur-md transition-colors hover:bg-neutral-900/80">
              <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-purple-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center mb-6 border border-purple-500/30 text-purple-400">
                  <Zap className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-white">Ngrok Webhooks</h3>
                <p className="text-neutral-400 text-sm">Secure local-to-cloud media tunneling ensuring zero downtime during Meta Graph API verification.</p>
              </div>
            </div>

            {/* Feature 3: Live CDP */}
            <div className="relative group overflow-hidden rounded-3xl bg-neutral-900/50 border border-white/10 p-8 flex flex-col justify-end backdrop-blur-md transition-colors hover:bg-neutral-900/80">
               <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity group-hover:scale-110 duration-700">
                <Users className="w-32 h-32 text-orange-500" />
              </div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center mb-6 border border-orange-500/30 text-orange-400">
                  <Activity className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold mb-2 text-white">Live CDP Polling</h3>
                <p className="text-neutral-400 text-sm">Real-time stream of audience interactions directly injected into the dashboard view.</p>
              </div>
            </div>

            {/* Feature 4: Fault Tolerance */}
            <div className="md:col-span-2 relative group overflow-hidden rounded-3xl bg-neutral-900/50 border border-white/10 p-8 flex flex-col justify-end backdrop-blur-md transition-colors hover:bg-neutral-900/80">
               <div className="absolute -bottom-10 right-10 flex gap-2 opacity-30 group-hover:opacity-60 transition-all duration-500 transform group-hover:-translate-y-4">
                 <div className="w-16 h-32 bg-green-500/20 rounded-t-xl border-t border-l border-r border-green-500/40"></div>
                 <div className="w-16 h-48 bg-blue-500/20 rounded-t-xl border-t border-l border-r border-blue-500/40"></div>
                 <div className="w-16 h-24 bg-red-500/20 rounded-t-xl border-t border-l border-r border-red-500/40"></div>
               </div>
              <div className="relative z-10">
                <div className="w-12 h-12 bg-green-500/20 rounded-xl flex items-center justify-center mb-6 border border-green-500/30 text-green-400">
                  <Shield className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold mb-2 text-white">Absolute Fault Tolerance</h3>
                <p className="text-neutral-400 max-w-md">Promise.allSettled fetching architecture ensures your core dashboard remains fully operational even if specific OAuth tokens expire.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer / Final CTA */}
      <footer className="relative z-10 py-24 px-6 md:px-12 border-t border-white/5 bg-black">
        <div className="max-w-4xl mx-auto text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl flex items-center justify-center shadow-lg shadow-orange-500/20 mb-8 blur-[2px] opacity-70">
            <Layers className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-4xl md:text-5xl font-black mb-6 tracking-tighter text-white">Ready to take control?</h2>
          <p className="text-neutral-400 mb-10 text-lg max-w-xl">
            Access the automation console to view analytics, monitor your queue, and execute multi-platform distributions instantly.
          </p>
          <SignedOut>
            <SignUpButton mode="modal">
              <button className="px-10 py-5 bg-white text-black rounded-full font-black text-lg transition-transform hover:scale-105 shadow-[0_0_40px_rgba(255,255,255,0.2)] flex items-center gap-2">
                Deploy Unified Marketing
                <ArrowRight className="w-5 h-5" />
              </button>
            </SignUpButton>
          </SignedOut>
          <SignedIn>
            <Link 
              href="/dashboard"
              className="px-10 py-5 bg-white text-black rounded-full font-black text-lg transition-transform hover:scale-105 shadow-[0_0_40px_rgba(255,255,255,0.2)] flex items-center gap-2"
            >
              Access Dashboard Protocol
              <ArrowRight className="w-5 h-5" />
            </Link>
          </SignedIn>
        </div>
        <div className="max-w-7xl mx-auto mt-24 pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center text-xs font-bold text-neutral-600 uppercase tracking-widest">
          <p>© 2026 Unified Marketing Automation OS</p>
          <div className="flex items-center gap-6 mt-4 md:mt-0">
             <span className="flex items-center gap-2 group cursor-pointer hover:text-green-500 transition-colors">
               <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)] group-hover:animate-pulse"></div>
               All Systems Operational
             </span>
             <span>v2.4.0</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
