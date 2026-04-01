'use client';

import CdpActivity from '@/components/CdpActivity';
import SystemHealth from '@/components/SystemHealth';

interface IntegrationViewProps {
    systemStatus: any;
}

export default function IntegrationView({ systemStatus }: IntegrationViewProps) {
    return (
        <div className="animate-in fade-in duration-500">
            <div className="mb-8">
                <h1 className="text-3xl font-black text-gray-900 tracking-tight">Integration Status</h1>
                <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mt-1">Real-time System Connectivity</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-green-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500"></div>
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">YouTube API</h3>
                            <div className="flex items-center gap-1.5">
                                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                                <span className="text-[10px] font-bold text-green-600 uppercase">Live</span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Latency</span>
                                <span className="text-gray-900 font-black">145ms</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Uptime</span>
                                <span className="text-gray-900 font-black">99.9%</span>
                            </div>
                            <div className="pt-4 border-t border-gray-50">
                                <p className="text-[10px] font-bold text-gray-400 uppercase">Daily Request Cap</p>
                                <div className="h-2 bg-gray-100 rounded-full mt-2">
                                    <div className="h-full bg-orange-500 w-1/4 rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500"></div>
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Database Cluster</h3>
                            <div className="flex items-center gap-1.5">
                                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                                <span className="text-[10px] font-bold text-green-600 uppercase">Healthy</span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Read Latency</span>
                                <span className="text-gray-900 font-black">23ms</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Connections</span>
                                <span className="text-gray-900 font-black">12/100</span>
                            </div>
                            <div className="pt-4 border-t border-gray-50">
                                <p className="text-[10px] font-bold text-gray-400 uppercase">Storage Capacity</p>
                                <div className="h-2 bg-gray-100 rounded-full mt-2">
                                    <div className="h-full bg-blue-500 w-[24%] rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-yellow-50 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-110 duration-500"></div>
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-8">
                            <h3 className="text-sm font-black text-gray-900 uppercase tracking-tight">Redis Cache</h3>
                            <div className="flex items-center gap-1.5">
                                <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                                <span className="text-[10px] font-bold text-yellow-600 uppercase">Warming</span>
                            </div>
                        </div>
                        <div className="space-y-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Hit Rate</span>
                                <span className="text-gray-900 font-black">87%</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-500 font-medium">Memory Usage</span>
                                <span className="text-gray-900 font-black">512MB / 1GB</span>
                            </div>
                            <div className="pt-4 border-t border-gray-50">
                                <p className="text-[10px] font-bold text-gray-400 uppercase">Sync Status</p>
                                <div className="animate-pulse h-2 bg-gray-100 rounded-full mt-2">
                                    <div className="h-full bg-yellow-500 w-[87%] rounded-full"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <CdpActivity />
                </div>
                <div className="lg:col-span-1">
                    <SystemHealth status={systemStatus} />
                </div>
            </div>
        </div>
    );
}
