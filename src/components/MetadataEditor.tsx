'use client';

import { useState, useEffect } from 'react';
import { X, CheckCircle2, AlertCircle, Info, ChevronRight, Hash, Eye, Globe, Lock } from 'lucide-react';
import { youtubeApi } from '@/services/api';

interface MetadataEditorProps {
  filename: string;
  initialData: {
    title: string;
    description: string;
    tags?: string[];
    visibility?: 'public' | 'unlisted' | 'private';
  };
  onSave: (data: any) => void;
  onClose: () => void;
}

export default function MetadataEditor({ filename, initialData, onSave, onClose }: MetadataEditorProps) {
  const [title, setTitle] = useState(initialData.title);
  const [description, setDescription] = useState(initialData.description);
  const [tags, setTags] = useState<string[]>(initialData.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [visibility, setVisibility] = useState(initialData.visibility || 'public');
  const [seoResult, setSeoResult] = useState<{ score: number; suggestions: string[] } | null>(null);
  const [loadingSeo, setLoadingSeo] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (title || description) {
        checkSeo();
      }
    }, 1000);
    return () => clearTimeout(timer);
  }, [title, description]);

  const checkSeo = async () => {
    try {
      setLoadingSeo(true);
      const res = await youtubeApi.seoCheck({ title, description });
      setSeoResult(res.data);
    } catch (err) {
      console.error('SEO Check failed:', err);
    } finally {
      setLoadingSeo(false);
    }
  };

  const handleAddTag = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput('');
    }
  };

  const removeTag = (tag: string) => {
    setTags(tags.filter(t => t !== tag));
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 50) return 'text-orange-500';
    return 'text-red-500';
  };

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[450px] bg-white shadow-2xl z-[100] border-l border-gray-100 flex flex-col animate-in slide-in-from-right duration-300">
      <div className="p-6 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
        <div>
          <h4 className="font-black text-gray-900 uppercase tracking-tighter text-lg">Metadata Pro</h4>
          <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">Refining: {filename}</p>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white rounded-xl transition-all border border-transparent hover:border-gray-200">
          <X className="w-5 h-5 text-gray-400" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        {/* SEO Score Meter */}
        <div className="p-4 bg-gray-900 rounded-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent" />
            <div className="relative z-10 flex items-center justify-between">
                <div>
                    <h5 className="text-[10px] font-black text-white uppercase tracking-widest mb-1">SEO Health Score</h5>
                    <div className="flex items-baseline gap-2">
                        <span className={`text-4xl font-black ${seoResult ? getScoreColor(seoResult.score) : 'text-gray-600'}`}>
                            {seoResult ? seoResult.score : '--'}
                        </span>
                        <span className="text-gray-500 text-xs font-bold">/ 100</span>
                    </div>
                </div>
                {loadingSeo ? (
                    <div className="w-12 h-12 border-2 border-orange-500/30 border-t-orange-500 rounded-full animate-spin" />
                ) : (
                    <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                        <Eye className="w-6 h-6 text-orange-400" />
                    </div>
                )}
            </div>
            {seoResult && seoResult.suggestions.length > 0 && (
                <div className="mt-4 pt-4 border-t border-white/5">
                    <p className="text-[9px] font-black text-orange-400 uppercase mb-2 tracking-tighter flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> Quick Optimization
                    </p>
                    <p className="text-[11px] text-gray-400 font-medium leading-relaxed italic">
                        "{seoResult.suggestions[0]}"
                    </p>
                </div>
            )}
        </div>

        {/* Title */}
        <section className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest">Video Title</label>
            <span className={`text-[10px] font-bold ${title.length > 100 ? 'text-red-500' : 'text-gray-400'}`}>
                {title.length}/100
            </span>
          </div>
          <input
            type="text"
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all font-bold text-gray-900"
            placeholder="A catchy, keyword-rich title..."
            value={title}
            onChange={e => setTitle(e.target.value)}
          />
        </section>

        {/* Description */}
        <section className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest">Description</label>
            <span className={`text-[10px] font-bold ${description.length > 5000 ? 'text-red-500' : 'text-gray-400'}`}>
                {description.length}/5000
            </span>
          </div>
          <textarea
            rows={5}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all font-medium text-gray-700 text-sm leading-relaxed"
            placeholder="Tell your viewers about your video..."
            value={description}
            onChange={e => setDescription(e.target.value)}
          />
        </section>

        {/* Tags */}
        <section className="space-y-3">
          <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest ml-1 flex items-center gap-1">
            <Hash className="w-3 h-3" /> Tags
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {tags.map(tag => (
              <span key={tag} className="inline-flex items-center gap-1.5 px-3 py-1 bg-orange-50 text-orange-600 border border-orange-100 rounded-lg text-xs font-bold group">
                {tag}
                <button onClick={() => removeTag(tag)} className="hover:text-red-500 transition-colors">
                    <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
          <input
            type="text"
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all text-sm font-medium"
            placeholder="Add tag and press Enter..."
            value={tagInput}
            onChange={e => setTagInput(e.target.value)}
            onKeyDown={handleAddTag}
          />
        </section>

        {/* Visibility */}
        <section className="space-y-3">
            <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest ml-1">Privacy Status</label>
            <div className="grid grid-cols-3 gap-3">
                {[
                    { id: 'public', label: 'Public', icon: Globe },
                    { id: 'unlisted', label: 'Unlisted', icon: ChevronRight },
                    { id: 'private', label: 'Private', icon: Lock },
                ].map((item: any) => (
                    <button
                        key={item.id}
                        onClick={() => setVisibility(item.id)}
                        className={`flex flex-col items-center gap-2 p-3 rounded-xl border transition-all ${
                            visibility === item.id 
                            ? 'bg-orange-50 border-orange-500 text-orange-600' 
                            : 'bg-white border-gray-100 text-gray-400 hover:border-gray-200'
                        }`}
                    >
                        <item.icon className="w-4 h-4" />
                        <span className="text-[10px] font-black uppercase tracking-tighter">{item.label}</span>
                    </button>
                ))}
            </div>
        </section>
      </div>

      <div className="p-6 border-t border-gray-100 bg-gray-50/50 flex gap-3">
        <button 
            onClick={onClose}
            className="flex-1 px-4 py-4 border border-gray-200 bg-white text-gray-600 rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-gray-50 transition-all"
        >
            Discard
        </button>
        <button 
            onClick={() => onSave({ title, description, tags, visibility })}
            className="flex-[2] px-4 py-4 bg-orange-600 text-white rounded-2xl text-[10px] font-black uppercase tracking-widest hover:bg-orange-700 transition-all shadow-lg active:scale-95"
        >
            Apply Changes
        </button>
      </div>
    </div>
  );
}
