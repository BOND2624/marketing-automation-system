'use client';

import { useState, useEffect } from 'react';
import { Play, CheckCircle2, XCircle, Clock, AlertCircle, X, ExternalLink, RefreshCw, Filter, Search } from 'lucide-react';
import { campaignApi } from '@/services/api';

interface Execution {
  id: number;
  campaign_name: string;
  status: 'success' | 'failed' | 'running' | 'pending';
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  results?: any;
}

export default function ExecutionHistoryEnhanced() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEx, setSelectedEx] = useState<Execution | null>(null);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const fetchExecutions = async () => {
    try {
      setLoading(true);
      const res = await campaignApi.getExecutions(20);
      setExecutions(res.data);
    } catch (err) {
      console.error('Failed to fetch executions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExecutions();
    const interval = setInterval(fetchExecutions, 30000); // Poll every 30s
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'running':
        return <Play className="w-5 h-5 text-blue-600 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-600" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-gray-400" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-50/50 border-green-100';
      case 'running':
        return 'bg-blue-50/50 border-blue-100';
      case 'failed':
        return 'bg-red-50/50 border-red-100';
      default:
        return 'bg-gray-50/50 border-gray-100';
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const filteredExecutions = executions.filter(ex => {
    const matchesSearch = ex.campaign_name.toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || ex.status === filter;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full relative overflow-hidden">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="font-bold text-gray-900">Recent Executions</h3>
          <p className="text-[10px] font-black uppercase text-gray-400 tracking-widest mt-1">Live Automation Status</p>
        </div>
        <div className="flex items-center gap-2">
            <div className="relative">
                <Search className="w-3 h-3 absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
                <input 
                    type="text" 
                    placeholder="Search..." 
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-8 pr-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-xs focus:ring-1 focus:ring-orange-500 outline-none w-32 focus:w-48 transition-all"
                />
            </div>
            <button 
                onClick={fetchExecutions}
                className={`p-1.5 hover:bg-gray-100 rounded-lg transition-colors ${loading ? 'animate-spin' : ''}`}
            >
                <RefreshCw className="w-4 h-4 text-gray-500" />
            </button>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2 scrollbar-hide">
        {['all', 'running', 'success', 'failed'].map((f) => (
            <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter border transition-all ${
                    filter === f 
                    ? 'bg-gray-900 border-gray-900 text-white' 
                    : 'bg-white border-gray-200 text-gray-500 hover:border-gray-300'
                }`}
            >
                {f}
            </button>
        ))}
      </div>

      <div className="space-y-2 flex-1 overflow-y-auto pr-1">
        {loading && executions.length === 0 ? (
            Array(5).fill(0).map((_, i) => (
                <div key={i} className="h-14 bg-gray-50 animate-pulse rounded-lg border border-gray-100" />
            ))
        ) : filteredExecutions.length === 0 ? (
            <div className="h-40 flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-100 rounded-xl">
                <Clock className="w-8 h-8 mb-2 opacity-20" />
                <p className="text-xs font-medium">No executions found</p>
            </div>
        ) : filteredExecutions.map((ex) => (
          <div
            key={ex.id}
            onClick={() => setSelectedEx(ex)}
            className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-all group hover:shadow-md hover:-translate-y-0.5 ${getStatusColor(
              ex.status,
            )}`}
          >
            <div className="shrink-0">{getStatusIcon(ex.status)}</div>

            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-gray-900 truncate">{ex.campaign_name}</p>
              <div className="flex items-center gap-2 mt-0.5">
                <p className="text-[10px] font-bold text-gray-500 uppercase">{formatTime(ex.created_at)}</p>
                {ex.status === 'failed' && (
                  <div className="flex items-center gap-1 px-1.5 py-0.5 bg-red-100 rounded-full">
                    <AlertCircle className="w-2.5 h-2.5 text-red-600" />
                    <span className="text-[10px] font-black uppercase text-red-600">Error</span>
                  </div>
                )}
              </div>
            </div>

            <div className="shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
               <div className="p-1.5 bg-white rounded-lg shadow-sm border border-gray-100">
                  <Play className="w-3 h-3 text-orange-500" />
               </div>
            </div>
          </div>
        ))}
      </div>

      {/* Detail Drawer */}
      {selectedEx && (
        <div className="absolute inset-0 z-50 flex justify-end animate-in slide-in-from-right duration-300">
            <div className="w-[85%] bg-white h-full shadow-2xl border-l border-gray-100 flex flex-col">
                <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                    <div>
                        <h4 className="font-black text-gray-900">Execution Details</h4>
                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mt-1">ID: #{selectedEx.id}</p>
                    </div>
                    <button 
                        onClick={() => setSelectedEx(null)}
                        className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-400" />
                    </button>
                </div>
                
                <div className="flex-1 overflow-y-auto p-6 space-y-6">
                    <section>
                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Status</p>
                        <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl border ${getStatusColor(selectedEx.status)}`}>
                            {getStatusIcon(selectedEx.status)}
                            <span className="text-xs font-black uppercase text-gray-700">{selectedEx.status}</span>
                        </div>
                    </section>

                    <section>
                        <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Campaign</p>
                        <p className="text-lg font-black text-gray-900">{selectedEx.campaign_name}</p>
                    </section>

                    <section className="grid grid-cols-2 gap-4">
                        <div>
                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Started</p>
                            <p className="text-sm font-bold text-gray-700">{selectedEx.started_at ? formatTime(selectedEx.started_at) : '---'}</p>
                        </div>
                        <div>
                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Duration</p>
                            <p className="text-sm font-bold text-gray-700">1.2s</p>
                        </div>
                    </section>

                    {selectedEx.error_message && (
                        <section className="p-4 bg-red-50 border border-red-100 rounded-xl">
                            <div className="flex items-center gap-2 text-red-600 mb-2">
                                <AlertCircle className="w-4 h-4" />
                                <span className="text-[10px] font-black uppercase">Failure Log</span>
                            </div>
                            <p className="text-xs text-red-700 font-mono leading-relaxed whitespace-pre-wrap">
                                {selectedEx.error_message}
                            </p>
                        </section>
                    )}

                    {selectedEx.results && Object.keys(selectedEx.results).length > 0 && (
                        <section>
                            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">Output Results</p>
                            <div className="p-4 bg-gray-50 rounded-xl border border-gray-100">
                                <pre className="text-[10px] text-gray-600 font-mono whitespace-pre-wrap">
                                    {JSON.stringify(selectedEx.results, null, 2)}
                                </pre>
                            </div>
                        </section>
                    )}
                </div>

                <div className="p-6 border-t border-gray-100 bg-gray-50/50 flex gap-3">
                    <button className="flex-1 bg-gray-900 text-white py-3 rounded-xl text-xs font-black uppercase tracking-widest hover:bg-black transition-all shadow-lg active:scale-95">
                        Retry Loop
                    </button>
                    <button className="p-3 border border-gray-200 bg-white rounded-xl hover:bg-gray-50 transition-all">
                        <ExternalLink className="w-4 h-4 text-gray-600" />
                    </button>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}
