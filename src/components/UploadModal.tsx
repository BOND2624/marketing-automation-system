import { useState, useRef } from 'react';
import { X, Upload, CheckCircle, FileVideo, Youtube } from 'lucide-react';
import { uploadsApi } from '@/services/api';

interface UploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onUploadSuccess: (video: any) => void;
}

export default function UploadModal({ isOpen, onClose, onUploadSuccess }: UploadModalProps) {
    const [currentStep, setCurrentStep] = useState<'upload' | 'details'>('upload');
    const [file, setFile] = useState<File | null>(null);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadedFilename, setUploadedFilename] = useState<string | null>(null);

    // Form State
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [tags, setTags] = useState('');
    const [privacy, setPrivacy] = useState('unlisted');
    const [isPublishing, setIsPublishing] = useState(false);

    const fileInputRef = useRef<HTMLInputElement>(null);

    if (!isOpen) return null;

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            // Auto start upload
            handleUpload(selectedFile);
        }
    };

    const handleUpload = async (fileToUpload: File) => {
        setIsUploading(true);
        setUploadProgress(0);

        try {
            const res = await uploadsApi.upload(fileToUpload, (progressEvent) => {
                const percentCompleted = Math.round((progressEvent.loaded * 100) / (progressEvent.total || 1));
                setUploadProgress(percentCompleted);
            });

            if (res.data.success) {
                setUploadedFilename(res.data.filename);
                setTitle(fileToUpload.name.replace(/\.[^/.]+$/, ""));
                setCurrentStep('details');
            }
        } catch (error) {
            console.error('Upload failed', error);
            alert('Upload failed. Please try again.');
            setFile(null);
        } finally {
            setIsUploading(false);
        }
    };

    const handlePublish = async () => {
        if (!uploadedFilename) return;

        setIsPublishing(true);
        try {
            const metadata = {
                title,
                description,
                tags: tags.split(',').map(t => t.trim()).filter(Boolean),
                privacy_status: privacy
            };

            const res = await uploadsApi.publish(uploadedFilename, metadata);

            if (res.data.success) {
                onUploadSuccess({
                    filename: uploadedFilename,
                    task_id: res.data.task_id,
                    status: 'publishing',
                    size_mb: file ? file.size / (1024 * 1024) : 0,
                    thumbnail: 'https://images.pexels.com/photos/4348401/pexels-photo-4348401.jpeg?auto=compress&cs=tinysrgb&w=200' // Placeholder
                });
                onClose();
                // Reset state
                setFile(null);
                setCurrentStep('upload');
                setTitle('');
                setDescription('');
            }
        } catch (error) {
            console.error('Publish failed', error);
            alert('Publishing failed. Check console.');
        } finally {
            setIsPublishing(false);
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                    <h3 className="font-bold text-gray-900 flex items-center gap-2">
                        <Youtube className="w-5 h-5 text-red-600" />
                        Upload to YouTube
                    </h3>
                    <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {currentStep === 'upload' ? (
                        <div className="space-y-6">
                            <div
                                className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center gap-4 hover:border-orange-400 hover:bg-orange-50/10 transition-colors cursor-pointer"
                                onClick={() => !isUploading && fileInputRef.current?.click()}
                            >
                                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center">
                                    <Upload className="w-8 h-8 text-orange-600" />
                                </div>
                                <div className="text-center">
                                    <p className="font-bold text-gray-900">Click to upload video</p>
                                    <p className="text-sm text-gray-500">MP4 or MOV (Max 100MB)</p>
                                </div>
                                <input
                                    type="file"
                                    ref={fileInputRef}
                                    onChange={handleFileSelect}
                                    accept=".mp4,.mov"
                                    className="hidden"
                                />
                            </div>

                            {isUploading && (
                                <div className="space-y-2">
                                    <div className="flex justify-between text-xs font-semibold text-gray-600">
                                        <span>Uploading...</span>
                                        <span>{uploadProgress}%</span>
                                    </div>
                                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-orange-500 transition-all duration-300 ease-out"
                                            style={{ width: `${uploadProgress}%` }}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="space-y-4">
                            <div className="flex items-center gap-3 p-3 bg-green-50 text-green-700 rounded-lg text-sm mb-4">
                                <CheckCircle className="w-4 h-4" />
                                <span className="font-medium">Upload Complete: {file?.name}</span>
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Title</label>
                                <input
                                    type="text"
                                    value={title}
                                    onChange={e => setTitle(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
                                    placeholder="Video Title"
                                />
                            </div>

                            <div>
                                <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Description</label>
                                <textarea
                                    value={description}
                                    onChange={e => setDescription(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 h-24 resize-none"
                                    placeholder="Tell viewers about your video..."
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Privacy</label>
                                    <select
                                        value={privacy}
                                        onChange={e => setPrivacy(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 bg-white"
                                    >
                                        <option value="private">Private</option>
                                        <option value="unlisted">Unlisted</option>
                                        <option value="public">Public</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs font-bold text-gray-700 uppercase mb-1">Tags</label>
                                    <input
                                        type="text"
                                        value={tags}
                                        onChange={e => setTags(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500"
                                        placeholder="vlog, tech, review"
                                    />
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-semibold text-gray-600 hover:text-gray-900 transition-colors"
                    >
                        Cancel
                    </button>

                    {currentStep === 'details' && (
                        <button
                            onClick={handlePublish}
                            disabled={isPublishing || !title}
                            className="px-6 py-2 bg-red-600 text-white text-sm font-bold rounded-lg hover:bg-red-700 transition-colors shadow-lg shadow-red-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isPublishing ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Publishing
                                </>
                            ) : (
                                <>
                                    Publish Video
                                </>
                            )}
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
