import React, { useState, useRef } from 'react';
import { UploadCloud, FileImage, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import type { Photo } from '../types';

interface DragDropUploaderProps {
  eventId: string;
  onUploadSuccess: (photos: Photo[]) => void;
}

interface FileStatus {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  errorMsg?: string;
}

export const DragDropUploader: React.FC<DragDropUploaderProps> = ({ eventId, onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [filesStatus, setFilesStatus] = useState<FileStatus[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif', 'image/heic'];
  const MAX_SIZE = 25 * 1024 * 1024; // 25MB

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const validateAndAddFiles = (newFiles: FileList | File[]) => {
    setGlobalError(null);
    const validStatuses: FileStatus[] = [];

    Array.from(newFiles).forEach((file) => {
      if (!ALLOWED_TYPES.includes(file.type.toLowerCase())) {
        setGlobalError(`File '${file.name}' has invalid format. Only JPG, PNG, WEBP, GIF, HEIC allowed.`);
        return;
      }
      if (file.size > MAX_SIZE) {
        setGlobalError(`File '${file.name}' exceeds maximum 25MB size limit.`);
        return;
      }
      validStatuses.push({
        file,
        progress: 0,
        status: 'pending',
      });
    });

    setFilesStatus((prev) => [...prev, ...validStatuses]);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndAddFiles(e.dataTransfer.files);
    }
  };

  const removeFile = (index: number) => {
    setFilesStatus((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadAllFiles = async () => {
    if (filesStatus.length === 0) return;
    setIsUploading(true);
    setGlobalError(null);

    const formData = new FormData();
    filesStatus.forEach((item) => {
      formData.append('files', item.file);
    });

    try {
      setFilesStatus((prev) => prev.map((f) => ({ ...f, status: 'uploading', progress: 50 })));
      const res = await api.post(`/events/${eventId}/photos`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setFilesStatus((prev) => prev.map((f) => ({ ...f, status: 'success', progress: 100 })));
      onUploadSuccess(res.data);
      setTimeout(() => {
        setFilesStatus([]);
        setIsUploading(false);
      }, 1200);
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Photo upload failed. Storage error.';
      setGlobalError(msg);
      setFilesStatus((prev) => prev.map((f) => ({ ...f, status: 'error', errorMsg: msg })));
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full glass-card p-6 rounded-2xl border border-slate-700/60 mb-8">
      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-sky-400 bg-sky-950/30 scale-[1.01]'
            : 'border-slate-700 hover:border-slate-500 bg-slate-900/40 hover:bg-slate-900/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp,image/gif,image/heic"
          className="hidden"
          onChange={(e) => e.target.files && validateAndAddFiles(e.target.files)}
        />
        <div className="flex flex-col items-center justify-center gap-3">
          <div className="p-3 rounded-full bg-sky-950/60 text-sky-400 border border-sky-800/50">
            <UploadCloud className="w-8 h-8" />
          </div>
          <div>
            <p className="text-base font-semibold text-slate-200">
              Drag & Drop your photos here, or <span className="text-sky-400 underline">browse</span>
            </p>
            <p className="text-xs text-slate-400 mt-1">Supports JPG, PNG, WEBP, GIF up to 25MB each</p>
          </div>
        </div>
      </div>

      {/* Global Error Notice */}
      {globalError && (
        <div className="mt-4 p-3 rounded-lg bg-red-950/60 border border-red-800/60 text-red-300 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-400 shrink-0" />
          <span>{globalError}</span>
        </div>
      )}

      {/* Staged File List */}
      {filesStatus.length > 0 && (
        <div className="mt-6 space-y-3">
          <div className="flex items-center justify-between text-sm font-semibold text-slate-300">
            <span>Staged Photos ({filesStatus.length})</span>
            {!isUploading && (
              <button
                onClick={() => setFilesStatus([])}
                className="text-xs text-slate-400 hover:text-red-400"
              >
                Clear all
              </button>
            )}
          </div>

          <div className="max-h-48 overflow-y-auto space-y-2 pr-1">
            {filesStatus.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 rounded-lg bg-slate-800/60 border border-slate-700/50 text-sm"
              >
                <div className="flex items-center gap-3 truncate pr-4">
                  <FileImage className="w-5 h-5 text-sky-400 shrink-0" />
                  <span className="text-slate-200 truncate font-medium">{item.file.name}</span>
                  <span className="text-xs text-slate-400">({(item.file.size / 1024).toFixed(1)} KB)</span>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {item.status === 'uploading' && (
                    <span className="text-xs text-sky-400 flex items-center gap-1">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" /> Uploading...
                    </span>
                  )}
                  {item.status === 'success' && (
                    <span className="text-xs text-emerald-400 flex items-center gap-1 font-semibold">
                      <CheckCircle className="w-4 h-4" /> Ready
                    </span>
                  )}
                  {item.status === 'pending' && !isUploading && (
                    <button
                      onClick={() => removeFile(idx)}
                      className="p-1 text-slate-400 hover:text-red-400 rounded transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-3 flex justify-end">
            <button
              onClick={uploadAllFiles}
              disabled={isUploading}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center gap-2 text-sm transition-all"
            >
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Uploading to Object Store...
                </>
              ) : (
                <>
                  <UploadCloud className="w-4 h-4" /> Upload {filesStatus.length} Photos
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
