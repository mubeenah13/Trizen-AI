import React, { useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Download, Calendar, User, FileText } from 'lucide-react';
import type { Photo, PublicPhoto } from '../types';

interface LightboxModalProps {
  photo: Photo | PublicPhoto | null;
  onClose: () => void;
  onPrev?: () => void;
  onNext?: () => void;
  hasPrev?: boolean;
  hasNext?: boolean;
}

export const LightboxModal: React.FC<LightboxModalProps> = ({
  photo,
  onClose,
  onPrev,
  onNext,
  hasPrev = false,
  hasNext = false,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowLeft' && onPrev && hasPrev) onPrev();
      if (e.key === 'ArrowRight' && onNext && hasNext) onNext();
    };
    if (photo) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'unset';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [photo, onClose, onPrev, onNext, hasPrev, hasNext]);

  if (!photo) return null;

  const isFullPhoto = 'uploaded_by' in photo;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/95 backdrop-blur-xl p-4 sm:p-8 animate-fade-in">
      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-6 right-6 p-2 rounded-full bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors z-50 border border-slate-700"
      >
        <X className="w-6 h-6" />
      </button>

      {/* Prev Button */}
      {hasPrev && onPrev && (
        <button
          onClick={onPrev}
          className="absolute left-6 p-3 rounded-full bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors z-50 border border-slate-700"
        >
          <ChevronLeft className="w-6 h-6" />
        </button>
      )}

      {/* Next Button */}
      {hasNext && onNext && (
        <button
          onClick={onNext}
          className="absolute right-6 p-3 rounded-full bg-slate-800/80 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors z-50 border border-slate-700"
        >
          <ChevronRight className="w-6 h-6" />
        </button>
      )}

      {/* Content Container */}
      <div className="max-w-6xl max-h-[90vh] w-full flex flex-col md:flex-row glass-card rounded-2xl overflow-hidden shadow-2xl border border-slate-800">
        <div className="flex-1 bg-black/80 flex items-center justify-center p-4 relative min-h-[300px] md:min-h-[500px]">
          <img
            src={photo.url}
            alt={photo.filename}
            className="max-h-[75vh] max-w-full object-contain rounded-lg shadow-xl"
          />
        </div>

        {/* Sidebar Info */}
        <div className="w-full md:w-80 p-6 bg-slate-900/90 flex flex-col justify-between border-t md:border-t-0 md:border-l border-slate-800">
          <div>
            <h4 className="text-lg font-bold text-slate-100 mb-2 truncate" title={photo.filename}>
              {photo.filename}
            </h4>

            <div className="space-y-3 mt-4 text-sm text-slate-300">
              {isFullPhoto && (photo as Photo).uploader_name && (
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4 text-sky-400" />
                  <span>Uploaded by: <strong className="text-slate-100">{(photo as Photo).uploader_name}</strong></span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span>Size: <strong>{(photo.file_size / 1024).toFixed(1)} KB</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-emerald-400" />
                <span>Date: {new Date(photo.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800">
            <a
              href={photo.url}
              download={photo.filename}
              target="_blank"
              rel="noreferrer"
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold shadow-lg shadow-sky-500/25 transition-all text-sm"
            >
              <Download className="w-4 h-4" /> Download Original
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};
