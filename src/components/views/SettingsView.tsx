'use client';

import { Users, Zap, CreditCard, Bell, AlertCircle, Plus, Activity, ShieldCheck } from 'lucide-react';

export default function SettingsView() {
    return (
        <div className="animate-in fade-in duration-500 max-w-5xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">System Settings</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Global Configuration & Identity</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-8">
                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 bg-orange-50 rounded-xl flex items-center justify-center">
                                <Users className="w-5 h-5 text-orange-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Identity Profile</h3>
                        </div>
                        <div className="space-y-6">
                            {[
                                { label: 'Admin Name', value: 'Rylie Command', type: 'text' },
                                { label: 'System Email', value: 'rylie@unified.ai', type: 'email' },
                                { label: 'Company Domain', value: 'unified-marketing.com', type: 'text' }
                            ].map((field, i) => (
                                <div key={i}>
                                    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">{field.label}</label>
                                    <input type={field.type} defaultValue={field.value} className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-sm font-bold text-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all" />
                                </div>
                            ))}
                            <button className="w-full py-4 bg-gray-900 text-white rounded-xl text-sm font-black uppercase tracking-widest hover:bg-orange-600 transition-colors mt-4">Save Identity</button>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                                <Zap className="w-5 h-5 text-blue-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">API Infrastructure</h3>
                        </div>
                        <div className="space-y-6">
                            <div className="p-4 bg-orange-50 rounded-xl border border-orange-100 flex items-start gap-4">
                                <AlertCircle className="w-5 h-5 text-orange-500 mt-1 shrink-0" />
                                <div>
                                    <p className="text-sm font-black text-orange-900 mb-1">Quota Warning</p>
                                    <p className="text-xs font-bold text-orange-700/70">Your YouTube API quota is nearing its weekly limit. Consider optimizing your sync intervals.</p>
                                </div>
                            </div>
                            <div>
                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">YouTube Secret Key</label>
                                <div className="flex gap-2">
                                    <input type="password" value="••••••••••••••••••••••••" readOnly className="flex-1 px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-sm font-bold text-gray-900" />
                                    <button className="px-4 py-3 bg-gray-100 text-gray-900 rounded-xl text-xs font-black uppercase hover:bg-gray-200 transition-colors">Rotate</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-8">
                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center">
                                <CreditCard className="w-5 h-5 text-purple-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Billing & Ops</h3>
                        </div>
                        <div className="space-y-6">
                            <div className="flex justify-between items-center p-6 bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl text-white">
                                <div>
                                    <p className="text-[10px] font-black opacity-50 uppercase tracking-widest mb-1">Current Plan</p>
                                    <h4 className="text-2xl font-black italic tracking-tighter uppercase">Professional <span className="text-orange-500">v2</span></h4>
                                </div>
                                <h4 className="text-2xl font-black">$299<span className="text-xs opacity-50">/mo</span></h4>
                            </div>
                            <button className="w-full py-4 border-2 border-dashed border-gray-100 rounded-xl text-sm font-black text-gray-400 uppercase tracking-widest hover:border-orange-500 hover:text-orange-500 transition-colors group">
                                <Plus className="w-4 h-4 inline-block mr-2 mb-1 group-hover:rotate-90 transition-transform" /> Add Payment Method
                            </button>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center">
                                <Bell className="w-5 h-5 text-red-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Signal Config</h3>
                        </div>
                        <div className="space-y-4">
                            {['Campaign Signal Alerts', 'Real-time Error Push', 'Weekly Strategy Digest', 'Security Login Emails'].map((item, i) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                                    <span className="text-sm font-bold text-gray-700">{item}</span>
                                    <div className="w-12 h-6 bg-green-500 rounded-full flex items-center px-1 cursor-pointer">
                                        <div className="w-4 h-4 bg-white rounded-full ml-auto shadow-sm"></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* System Infrastructure Debug */}
                    <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800 shadow-2xl overflow-hidden relative group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Activity className="w-24 h-24 text-white" />
                        </div>
                        <div className="flex items-center gap-3 mb-8 relative">
                            <div className="w-10 h-10 bg-green-500/10 rounded-xl flex items-center justify-center border border-green-500/20">
                                <ShieldCheck className="w-5 h-5 text-green-500" />
                            </div>
                            <div>
                                <h3 className="text-sm font-black text-white uppercase tracking-tight">Infrastructure Pulse</h3>
                                <p className="text-[9px] font-bold text-green-500/50 uppercase tracking-widest">Active Debug Console</p>
                            </div>
                        </div>

                        <div className="space-y-4 font-mono">
                            <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">Worker Asset Root (Absolute)</p>
                                <code className="text-[11px] text-green-400 break-all bg-black/50 px-2 py-1 rounded block">
                                    /Users/pranavshinde/Developer/marketing-automation-system/uploads
                                </code>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                    <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">OAuth2 Token</p>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                                        <span className="text-[10px] font-bold text-white uppercase">Detected</span>
                                    </div>
                                </div>
                                <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                    <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">Venv Path</p>
                                    <span className="text-[10px] font-bold text-gray-400 uppercase">./venv/bin/python</span>
                                </div>
                            </div>

                            <div className="flex items-center justify-between px-2 pt-2">
                                <span className="text-[10px] font-bold text-gray-600 uppercase">Latency: 42ms</span>
                                <span className="text-[10px] font-bold text-gray-600 uppercase">Redis: Connected</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
