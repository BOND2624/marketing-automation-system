'use client';

import { Users, Zap, CreditCard, Bell, AlertCircle, Plus, Activity, ShieldCheck, Youtube, Facebook, Instagram, LogOut, CheckCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { youtubeApi, metaApi } from '@/services/api';

export default function SettingsView() {
    const [ytStatus, setYtStatus] = useState<any>(null);
    const [metaStatus, setMetaStatus] = useState<any>(null);
    const [tokenInput, setTokenInput] = useState('');
    const [metaInput, setMetaInput] = useState({ accessToken: '', pageId: '', igId: '' });
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ text: string, type: 'error' | 'success' } | null>(null);

    const fetchStatus = async () => {
        try {
            const [ytRes, metaRes] = await Promise.all([
                youtubeApi.getStatus(),
                metaApi.getStatus()
            ]);
            setYtStatus(ytRes.data);
            setMetaStatus(metaRes.data);
        } catch (err) {
            console.error('Failed to fetch status:', err);
        }
    };

    useEffect(() => {
        fetchStatus();
    }, []);

    const handleConnectYT = async () => {
        if (!tokenInput) return;
        setIsLoading(true);
        setMessage(null);
        try {
            const res = await youtubeApi.updateAuth(tokenInput);
            setMessage({ text: res.data.message, type: 'success' });
            setTokenInput('');
            fetchStatus();
        } catch (err: any) {
            setMessage({ text: err.response?.data?.detail || 'Failed to connect YouTube', type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleConnectMeta = async () => {
        if (!metaInput.accessToken) return;
        setIsLoading(true);
        setMessage(null);
        try {
            const res = await metaApi.updateAuth({
                access_token: metaInput.accessToken,
                page_id: metaInput.pageId,
                instagram_business_id: metaInput.igId
            });
            setMessage({ text: res.data.message, type: 'success' });
            setMetaInput({ accessToken: '', pageId: '', igId: '' });
            fetchStatus();
        } catch (err: any) {
            setMessage({ text: err.response?.data?.detail || 'Failed to connect Meta', type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleDisconnectYT = async () => {
        if (!confirm('Are you sure you want to disconnect YouTube?')) return;
        setIsLoading(true);
        try {
            await youtubeApi.disconnect();
            setMessage({ text: 'YouTube account disconnected', type: 'success' });
            fetchStatus();
        } catch (err) {
            setMessage({ text: 'Failed to disconnect', type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    const handleDisconnectMeta = async () => {
        if (!confirm('Are you sure you want to disconnect Meta (FB/IG)?')) return;
        setIsLoading(true);
        try {
            await metaApi.disconnect();
            setMessage({ text: 'Meta accounts disconnected', type: 'success' });
            fetchStatus();
        } catch (err) {
            setMessage({ text: 'Failed to disconnect Meta', type: 'error' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="animate-in fade-in duration-500 max-w-5xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">System Settings</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Global Configuration & Identity</p>
            </div>

            {message && (
                <div className={`mb-6 p-4 rounded-xl border flex items-center gap-3 animate-in slide-in-from-top-4 ${
                    message.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700'
                }`}>
                    {message.type === 'error' ? <AlertCircle className="w-5 h-5" /> : <CheckCircle className="w-5 h-5" />}
                    <span className="text-sm font-bold">{message.text}</span>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-8">
                    {/* YouTube Connection Card */}
                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm relative overflow-hidden group">
                         <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Youtube className="w-32 h-32 text-orange-600 -rotate-12" />
                        </div>
                        
                        <div className="flex items-center gap-3 mb-8 relative">
                            <div className="w-10 h-10 bg-orange-50 rounded-xl flex items-center justify-center">
                                <Youtube className="w-5 h-5 text-orange-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">YouTube Channel</h3>
                        </div>

                        {ytStatus?.is_valid ? (
                            <div className="space-y-6 relative">
                                <div className="p-4 bg-green-50 rounded-xl border border-green-100 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-5 h-5 text-green-500" />
                                        <div>
                                            <p className="text-sm font-black text-green-900 uppercase tracking-tight">Channel Connected</p>
                                            <p className="text-[10px] font-bold text-green-700">Token status: {ytStatus.status}</p>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={handleDisconnectYT}
                                        disabled={isLoading}
                                        className="p-2 hover:bg-red-100 text-red-500 rounded-lg transition-colors"
                                    >
                                        <LogOut className="w-5 h-5" />
                                    </button>
                                </div>
                                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest leading-relaxed">
                                    Your system is currently authorized to publish and fetch analytics for the connected channel.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-6 relative">
                                <div className="p-4 bg-red-50 rounded-xl border border-red-100 flex items-start gap-4">
                                    <AlertCircle className="w-5 h-5 text-red-500 mt-1 shrink-0" />
                                    <div>
                                        <p className="text-sm font-black text-red-900 mb-1">Account Required</p>
                                        <p className="text-xs font-bold text-red-700/70">Connect your YouTube account to enable automated publishing and global analytics.</p>
                                    </div>
                                </div>
                                
                                <div>
                                    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-2">OAuth Token JSON</label>
                                    <textarea 
                                        rows={4}
                                        value={tokenInput}
                                        onChange={(e) => setTokenInput(e.target.value)}
                                        placeholder='Paste your "youtube_token.json" content here...'
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-[11px] font-mono text-gray-900 focus:outline-none focus:ring-2 focus:ring-orange-500/20 transition-all resize-none"
                                    />
                                </div>
                                
                                <button 
                                    onClick={handleConnectYT}
                                    disabled={isLoading || !tokenInput}
                                    className="w-full py-4 bg-orange-600 text-white rounded-xl text-sm font-black uppercase tracking-widest hover:bg-orange-700 transition-colors shadow-lg shadow-orange-600/20 flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 fill-white" />}
                                    Establish Connection
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Meta Connection Card */}
                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm relative overflow-hidden group">
                         <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Facebook className="w-32 h-32 text-blue-600 -rotate-12" />
                        </div>
                        
                        <div className="flex items-center gap-3 mb-8 relative">
                            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                                <Facebook className="w-5 h-5 text-blue-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Meta Identity (FB/IG)</h3>
                        </div>

                        {metaStatus?.is_valid ? (
                            <div className="space-y-6 relative">
                                <div className="p-4 bg-blue-50 rounded-xl border border-blue-100 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-5 h-5 text-blue-500" />
                                        <div>
                                            <p className="text-sm font-black text-blue-900 uppercase tracking-tight">Accounts Connected</p>
                                            <p className="text-[10px] font-bold text-blue-700">Status: {metaStatus.status}</p>
                                        </div>
                                    </div>
                                    <button 
                                        onClick={handleDisconnectMeta}
                                        disabled={isLoading}
                                        className="p-2 hover:bg-red-100 text-red-500 rounded-lg transition-colors"
                                    >
                                        <LogOut className="w-5 h-5" />
                                    </button>
                                </div>
                                <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest leading-relaxed">
                                    Successfully linked. You can now publish and sync data across Facebook and Instagram.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-4 relative">
                                <div>
                                    <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">User Access Token</label>
                                    <input 
                                        type="password"
                                        value={metaInput.accessToken}
                                        onChange={(e) => setMetaInput({...metaInput, accessToken: e.target.value})}
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-xs font-bold text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                                        placeholder="EAApTscmMeSQ..."
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">Page ID</label>
                                        <input 
                                            value={metaInput.pageId}
                                            onChange={(e) => setMetaInput({...metaInput, pageId: e.target.value})}
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-xs font-bold text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                                            placeholder="9567209..."
                                        />
                                    </div>
                                    <div>
                                        <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">Instagram ID</label>
                                        <input 
                                            value={metaInput.igId}
                                            onChange={(e) => setMetaInput({...metaInput, igId: e.target.value})}
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-xs font-bold text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all"
                                            placeholder="178414..."
                                        />
                                    </div>
                                </div>
                                <button 
                                    onClick={handleConnectMeta}
                                    disabled={isLoading || !metaInput.accessToken}
                                    className="w-full py-4 bg-blue-600 text-white rounded-xl text-sm font-black uppercase tracking-widest hover:bg-blue-700 transition-colors shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 disabled:opacity-50"
                                >
                                    {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 fill-white" />}
                                    Sync Meta Identity
                                </button>
                            </div>
                        )}
                    </div>

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
                            <button className="w-full py-4 bg-gray-900 text-white rounded-xl text-sm font-black uppercase tracking-widest hover:bg-orange-600 transition-colors mt-4 shadow-sm">Save Identity</button>
                        </div>
                    </div>
                </div>

                <div className="space-y-8">
                    <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                        <div className="flex items-center gap-3 mb-8">
                            <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center">
                                <Zap className="w-5 h-5 text-blue-500" />
                            </div>
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Signal Infrastructure</h3>
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
                                <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1.5">System Secret Key</label>
                                <div className="flex gap-2">
                                    <input type="password" value="••••••••••••••••••••••••" readOnly className="flex-1 px-4 py-3 bg-gray-50 border border-gray-100 rounded-xl text-xs font-bold text-gray-900" />
                                    <button className="px-4 py-3 bg-gray-100 text-gray-900 rounded-xl text-[10px] font-black uppercase hover:bg-gray-200 transition-colors">Rotate</button>
                                </div>
                            </div>
                        </div>
                    </div>

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
                                <h4 className="text-2xl font-black italic tracking-tighter">$299<span className="text-xs opacity-50">/mo</span></h4>
                            </div>
                            <button className="w-full py-4 border-2 border-dashed border-gray-100 rounded-xl text-sm font-black text-gray-400 uppercase tracking-widest hover:border-orange-500 hover:text-orange-500 transition-colors group">
                                <Plus className="w-4 h-4 inline-block mr-2 mb-1 group-hover:rotate-90 transition-transform" /> Add Payment Method
                            </button>
                        </div>
                    </div>

                    {/* System Infrastructure Pulse */}
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
                                <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">Worker Asset Root</p>
                                <code className="text-[10px] text-green-400 break-all bg-black/50 px-2 py-1 rounded block">
                                    /Users/pranavshinde/Developer/unified-marketing-automation-system/uploads
                                </code>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                    <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">YouTube Auth</p>
                                    <div className="flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full animate-pulse ${ytStatus?.token_exists ? 'bg-green-500' : 'bg-red-500'}`} />
                                        <span className="text-[10px] font-bold text-white uppercase">{ytStatus?.token_exists ? 'Found' : 'Missing'}</span>
                                    </div>
                                </div>
                                <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                    <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">Meta Auth</p>
                                    <div className="flex items-center gap-2">
                                        <div className={`w-2 h-2 rounded-full animate-pulse ${metaStatus?.token_exists ? 'bg-green-500' : 'bg-red-500'}`} />
                                        <span className="text-[10px] font-bold text-white uppercase">{metaStatus?.token_exists ? 'Found' : 'Missing'}</span>
                                    </div>
                                </div>
                                <div className="p-4 bg-black/40 rounded-xl border border-white/5">
                                    <p className="text-[10px] font-black text-gray-500 uppercase mb-2 tracking-widest">Venv Status</p>
                                     <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-green-500" />
                                        <span className="text-[10px] font-bold text-gray-400 uppercase">./venv Active</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
