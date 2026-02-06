'use client';

import { Users, BarChart3, Zap, Activity, ArrowRight, PlayCircle, Share2 } from 'lucide-react';
import StatCard from '@/components/StatCard';

export default function CustomerCdpView() {
    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">Customer Data Platform</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Audience Intelligence & Segmentation</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <StatCard title="Total Customers" value="24,512" change="+3.2%" changeLabel="Growth" icon={<Users className="w-5 h-5 text-blue-600" />} iconBg="bg-blue-50" />
                <StatCard title="Active Segments" value="18" change="2 New" changeLabel="This week" icon={<BarChart3 className="w-5 h-5 text-purple-600" />} iconBg="bg-purple-50" />
                <StatCard title="Engagement Cap" value="84%" change="+1.2%" changeLabel="Optimized" icon={<Zap className="w-5 h-5 text-yellow-600" />} iconBg="bg-yellow-50" />
                <StatCard title="Lifecycle Burn" value="2.3%" change="-0.4%" changeLabel="Churn Reduction" icon={<Activity className="w-5 h-5 text-red-600" />} iconBg="bg-red-50" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                    <h3 className="text-sm font-black uppercase text-gray-900 tracking-tight mb-6">Customer Segments</h3>
                    <div className="space-y-4">
                        {[
                            { name: 'Premium High LTV', count: '4,250', percent: 17, color: 'bg-orange-500' },
                            { name: 'Active Techies', count: '12,800', percent: 52, color: 'bg-blue-500' },
                            { name: 'Casual Browsers', count: '7,450', percent: 30, color: 'bg-green-500' }
                        ].map((seg, i) => (
                            <div key={i} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer group">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${seg.color}`}></div>
                                    <div>
                                        <p className="text-sm font-bold text-gray-900">{seg.name}</p>
                                        <p className="text-[10px] font-bold text-gray-400 uppercase">{seg.count} Customers</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    <span className="text-sm font-black text-gray-900">{seg.percent}%</span>
                                    <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-gray-900 transition-colors" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
                    <h3 className="text-sm font-black uppercase text-gray-900 tracking-tight mb-6">Audience Insights</h3>
                    <div className="space-y-6">
                        {[
                            { label: 'Email Engagement', value: 72, icon: <Activity className="w-4 h-4 text-orange-500" /> },
                            { label: 'Video Completion', value: 65, icon: <PlayCircle className="w-4 h-4 text-blue-500" /> },
                            { label: 'Social Sharing', value: 38, icon: <Share2 className="w-4 h-4 text-green-500" /> }
                        ].map((insight, i) => (
                            <div key={i}>
                                <div className="flex justify-between items-center mb-2">
                                    <div className="flex items-center gap-2">
                                        {insight.icon}
                                        <span className="text-[10px] font-black uppercase text-gray-500">{insight.label}</span>
                                    </div>
                                    <span className="text-sm font-black text-gray-900">{insight.value}%</span>
                                </div>
                                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                    <div className={`h-full bg-orange-500 rounded-full transition-all duration-1000`} style={{ width: `${insight.value}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
