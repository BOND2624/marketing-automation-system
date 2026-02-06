import { TrendingUp, ArrowUpRight } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  changeLabel: string;
  icon: React.ReactNode;
  iconBg: string;
}

export default function StatCard({ title, value, change, changeLabel, icon, iconBg }: StatCardProps) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-gray-100 hover:border-orange-200 transition-all duration-300 group hover:shadow-xl hover:shadow-orange-500/5 cursor-pointer relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <ArrowUpRight className="w-4 h-4 text-orange-400" />
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className={`w-12 h-12 ${iconBg} rounded-xl flex items-center justify-center transition-transform group-hover:scale-110 duration-300 shadow-sm`}>
          {icon}
        </div>
        <div>
          <p className="text-[10px] font-black uppercase text-gray-400 tracking-wider mb-0.5">{title}</p>
          <div className="flex items-center gap-1.5 text-green-600">
            <TrendingUp className="w-3 h-3" />
            <span className="text-[10px] font-black uppercase">{change}</span>
          </div>
        </div>
      </div>

      <div className="flex items-end justify-between">
        <h3 className="text-3xl font-black text-gray-900 tracking-tight group-hover:text-orange-600 transition-colors">
          {value}
        </h3>
        <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tighter mb-1.5">{changeLabel}</p>
      </div>
    </div>
  );
}
