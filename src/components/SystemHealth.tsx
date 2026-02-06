import { Database, Server, Youtube, CheckCircle2, XCircle } from 'lucide-react';

export default function SystemHealth({ status }: { status: any }) {
    const checkStatus = (svc: string) => {
        return status?.[svc] === 'active' || status?.[svc] === 'online' || status?.[svc] === true;
    };

    const StatusRow = ({ icon: Icon, label, svc, sublabel }: any) => {
        const isActive = checkStatus(svc);
        return (
            <div className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700">
                <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${svc === 'youtube' ? 'text-red-500' : svc === 'database' ? 'text-blue-400' : 'text-orange-400'}`} />
                    <span className="text-sm font-medium">{label}</span>
                </div>
                <div className="flex items-center gap-2">
                    {isActive ? (
                        <>
                            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                            <span className="text-xs text-green-400">{sublabel || 'Active'}</span>
                        </>
                    ) : (
                        <>
                            <div className="w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]" />
                            <span className="text-xs text-red-400">Error</span>
                        </>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="bg-gray-900 rounded-xl p-6 text-white h-full">
            <div className="mb-6">
                <h3 className="font-bold text-lg">System Health</h3>
                <p className="text-gray-400 text-sm">Real-time status checks</p>
            </div>

            <div className="space-y-4">
                <StatusRow icon={Database} label="PostgreSQL" svc="database" sublabel="Connected" />
                <StatusRow icon={Server} label="Redis Worker" svc="celery" sublabel="Active" />
                <StatusRow icon={Youtube} label="YouTube Auth" svc="youtube" sublabel="Valid" />
            </div>
        </div>
    );
}
