import { useState, useEffect, useRef } from 'react';
import { Play, CheckCircle, UploadCloud, Eye, Trash2, AlertCircle, X, Loader2 } from 'lucide-react';
import { uploadsApi, youtubeApi } from '@/services/api';

interface VideoItem {
  filename: string;
  size_mb: number;
  status: 'ready' | 'uploading' | 'publishing' | 'done' | 'failed';
  progress?: number;
  task_id?: string;
  error?: string;
  thumbnail?: string;
}

interface UploadQueueProps {
  videos: VideoItem[];
  setVideos: React.Dispatch<React.SetStateAction<VideoItem[]>>;
  ytAuthValid: boolean | null;
}

export default function UploadQueue({ videos, setVideos, ytAuthValid }: UploadQueueProps) {
  const [selectedVideos, setSelectedVideos] = useState<string[]>([]);
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [currentPublishing, setCurrentPublishing] = useState<{ filename: string; title: string; description: string; isShort: boolean } | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const updateVideoStatus = (filename: string, updates: Partial<VideoItem>) => {
    setVideos(prev => prev.map(v => v.filename === filename ? { ...v, ...updates } : v));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validation
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!['mp4', 'mov'].includes(ext || '')) {
      showToast('Only .mp4 and .mov formats are supported', 'error');
      return;
    }

    // Optimistic UI
    const newVideo: VideoItem = {
      filename: file.name,
      size_mb: Math.round(file.size / (1024 * 1024)),
      status: 'uploading',
      progress: 0,
      thumbnail: URL.createObjectURL(file) // Local preview
    };
    setVideos(prev => [newVideo, ...prev]);

    try {
      await uploadsApi.upload(file, (progressEvent) => {
        const percent = Math.round((progressEvent.loaded * 100) / (progressEvent.total || file.size));
        updateVideoStatus(file.name, { progress: percent });
      });
      updateVideoStatus(file.name, { status: 'ready', progress: undefined });
      showToast('File uploaded successfully', 'success');
    } catch (error) {
      console.error('Upload failed:', error);
      updateVideoStatus(file.name, { status: 'failed', error: 'Server upload failed' });
      showToast('Upload failed', 'error');
    }
  };

  const handlePublishClick = (video: VideoItem) => {
    if (!ytAuthValid) {
      showToast('Please connect YouTube in Settings first', 'error');
      return;
    }
    setCurrentPublishing({
      filename: video.filename,
      title: video.filename.replace(/\.[^/.]+$/, ""), // Default title
      description: "Uploaded via Unified Marketing Command",
      isShort: false
    });
    setShowMetadataModal(true);
  };

  const startPublishing = async () => {
    if (!currentPublishing) return;
    const { filename, title, description, isShort } = currentPublishing;

    updateVideoStatus(filename, { status: 'publishing' });
    setShowMetadataModal(false);

    try {
      const res = await uploadsApi.publish(filename, {
        title,
        description,
        upload_type: isShort ? 'short' : 'video'
      });
      updateVideoStatus(filename, { task_id: res.data.task_id });
    } catch (error: any) {
      updateVideoStatus(filename, { status: 'failed', error: error.response?.data?.detail || 'Publishing failed' });
    }
  };

  const showToast = (message: string, type: 'error' | 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const toggleSelect = (id: string) => {
    setSelectedVideos(prev =>
      prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]
    );
  };

  return (
    <div className="bg-white rounded-xl p-6 border border-gray-100 flex flex-col h-full min-h-[500px] shadow-sm relative">
      {/* Toast Notification */}
      {toast && (
        <div className={`absolute top-4 right-4 z-50 animate-in fade-in slide-in-from-top-4 px-4 py-3 rounded-lg shadow-xl flex items-center gap-3 border ${toast.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-700'
          }`}>
          {toast.type === 'error' ? <AlertCircle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />}
          <span className="text-sm font-bold">{toast.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="font-bold text-gray-900 border-l-4 border-orange-500 pl-3 uppercase tracking-tighter">Upload Queue</h3>
          <p className="text-[10px] text-gray-500 uppercase font-black tracking-widest mt-1 ml-3">
            {videos.length} Identified Assets
          </p>
        </div>
        <div className="flex gap-2">
          {!ytAuthValid && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 bg-red-50 text-red-600 rounded-lg border border-red-100">
              <AlertCircle className="w-3.5 h-3.5" />
              <span className="text-[10px] font-black uppercase">YouTube Disconnected</span>
            </div>
          )}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".mp4,.mov"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-4 py-2 text-xs font-bold bg-gray-900 text-white rounded-lg hover:bg-black transition-all shadow-sm flex items-center gap-2"
          >
            <UploadCloud className="w-4 h-4" />
            Bulk Upload
          </button>
        </div>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-2 gap-4 flex-1 overflow-y-auto pr-1">
        {videos.map((video) => (
          <div
            key={video.filename}
            className={`group relative overflow-hidden rounded-2xl border transition-all duration-300 ${video.status === 'uploading' ? 'opacity-70' : ''} border-gray-100 hover:border-orange-200 hover:shadow-md`}
          >
            <div className="relative aspect-video bg-gray-100 overflow-hidden">
              <img
                src={video.thumbnail || 'https://images.pexels.com/photos/3568520/pexels-photo-3568520.jpeg?auto=compress&cs=tinysrgb&w=200'}
                alt={video.filename}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700"
              />

              {/* Progress/Status Overlays */}
              <div className="absolute inset-0 bg-black/20 group-hover:bg-black/40 transition-colors" />

              {video.status === 'uploading' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-sm px-6">
                  <div className="w-full bg-white/20 h-1.5 rounded-full overflow-hidden mb-3">
                    <div
                      className="bg-orange-500 h-full transition-all duration-300"
                      style={{ width: `${video.progress}%` }}
                    />
                  </div>
                  <span className="text-white text-[10px] font-black uppercase tracking-widest">{video.progress}% Uploading</span>
                </div>
              )}

              {video.status === 'publishing' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-orange-600/60 backdrop-blur-sm animate-pulse">
                  <Loader2 className="w-8 h-8 text-white animate-spin mb-2" />
                  <span className="text-white text-[10px] font-black uppercase tracking-widest">In Queue</span>
                </div>
              )}

              {video.status === 'done' && (
                <div className="absolute top-3 right-3 z-10">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                    <CheckCircle className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}

              {video.status === 'failed' && (
                <div className="absolute top-3 right-3 z-10" title={video.error}>
                  <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center shadow-lg border-2 border-white">
                    <AlertCircle className="w-5 h-5 text-white" />
                  </div>
                </div>
              )}
            </div>

            <div className="p-4 bg-white">
              <h4 className="text-[13px] font-bold text-gray-900 truncate">
                {video.filename}
              </h4>
              <div className="flex items-center justify-between mt-3">
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-tight">{video.size_mb} MB</p>
                <div className="flex items-center gap-1">
                  {video.status === 'done' ? (
                    <span className="text-[10px] font-black uppercase text-green-600 bg-green-50 px-2 py-0.5 rounded-md border border-green-100">
                      Published
                    </span>
                  ) : video.status === 'publishing' ? (
                    <span className="text-[10px] font-black uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md border border-blue-100 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
                      Sending to YT
                    </span>
                  ) : video.status === 'failed' ? (
                    <button
                      onClick={() => handlePublishClick(video)}
                      className="text-[10px] font-black uppercase text-red-600 bg-red-50 px-2.5 py-1 rounded-md hover:bg-red-600 hover:text-white transition-all border border-red-100"
                    >
                      Retry
                    </button>
                  ) : (
                    <button
                      disabled={video.status === 'uploading'}
                      onClick={() => handlePublishClick(video)}
                      className="text-[10px] font-black uppercase text-orange-600 bg-orange-50 px-2.5 py-1 rounded-md hover:bg-orange-600 hover:text-white transition-all border border-orange-100 disabled:opacity-50"
                    >
                      Publish
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {videos.length === 0 && (
          <div className="col-span-2 flex flex-col items-center justify-center py-20 text-center bg-gray-50/50 rounded-2xl border-2 border-dashed border-gray-100">
            <UploadCloud className="w-10 h-10 text-orange-200 mb-4" />
            <p className="text-sm font-bold text-gray-900 mb-1">Queue is Clear</p>
            <p className="text-xs text-gray-500">Import your assets to begin the sequence.</p>
          </div>
        )}
      </div>

      {/* Metadata Modal */}
      {showMetadataModal && currentPublishing && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-300">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-300">
            <div className="p-6 border-b border-gray-100 flex items-center justify-between">
              <div>
                <h4 className="font-black text-gray-900 uppercase tracking-tighter text-lg">YouTube Metadata</h4>
                <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">Finalizing Broadcast Settings</p>
              </div>
              <button onClick={() => setShowMetadataModal(false)} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <div className="p-8 space-y-6">
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest ml-1">Video Title</label>
                <input
                  type="text"
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all font-bold text-gray-900"
                  value={currentPublishing.title}
                  onChange={e => setCurrentPublishing({ ...currentPublishing, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <label className="text-[10px] font-black uppercase text-gray-500 tracking-widest ml-1">Description</label>
                <textarea
                  rows={3}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-orange-500 outline-none transition-all font-medium text-gray-700 text-sm"
                  value={currentPublishing.description}
                  onChange={e => setCurrentPublishing({ ...currentPublishing, description: e.target.value })}
                />
              </div>

              {/* Post as Short Toggle */}
              <div className="flex items-center justify-between p-4 bg-orange-50/50 rounded-2xl border border-orange-100/50 group cursor-pointer"
                onClick={() => setCurrentPublishing({ ...currentPublishing, isShort: !currentPublishing.isShort })}>
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg transition-colors ${currentPublishing.isShort ? 'bg-orange-500 text-white' : 'bg-white text-orange-500 border border-orange-100'}`}>
                    <Play className="w-4 h-4 rotate-90" />
                  </div>
                  <div>
                    <h5 className="text-[11px] font-black uppercase text-gray-900 tracking-tight">Post as YouTube Short</h5>
                    <p className="text-[9px] font-bold text-gray-500 uppercase">Enables 60s vertical optimization</p>
                  </div>
                </div>
                <div className={`w-10 h-5 rounded-full relative transition-colors duration-300 ${currentPublishing.isShort ? 'bg-orange-500' : 'bg-gray-200'}`}>
                  <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all duration-300 ${currentPublishing.isShort ? 'left-6' : 'left-1'}`} />
                </div>
              </div>

              <button
                onClick={startPublishing}
                className="w-full py-4 bg-orange-600 text-white rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-orange-700 transition-all shadow-lg hover:shadow-orange-200 transform hover:-translate-y-1 active:translate-y-0"
              >
                Push to YouTube
              </button>
              <p className="text-center text-[9px] text-gray-400 font-bold uppercase tracking-tighter">This action uses 1,600 units of your daily API quota.</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
