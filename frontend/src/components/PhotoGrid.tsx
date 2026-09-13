import React, { useState } from 'react';
import { Check, CheckSquare, Square, Eye, Trash2, User } from 'lucide-react';
import type { Photo } from '../types';
import { LightboxModal } from './LightboxModal';

interface PhotoGridProps {
  photos: Photo[];
  selectedPhotoIds?: string[];
  onToggleSelectPhoto?: (photoId: string) => void;
  onSelectAll?: () => void;
  onDeselectAll?: () => void;
  onDeletePhoto?: (photoId: string) => void;
  selectable?: boolean;
}

export const PhotoGrid: React.FC<PhotoGridProps> = ({
  photos,
  selectedPhotoIds = [],
  onToggleSelectPhoto,
  onSelectAll,
  onDeselectAll,
  onDeletePhoto,
  selectable = false,
}) => {
  const [activePhotoIndex, setActivePhotoIndex] = useState<number | null>(null);

  if (photos.length === 0) {
    return (
      <div className="glass-card p-12 rounded-2xl text-center border border-slate-800">
        <p className="text-slate-400 font-medium">No photographs uploaded for this event yet.</p>
      </div>
    );
  }

  const isAllSelected = selectable && photos.length > 0 && selectedPhotoIds.length === photos.length;

  return (
    <div>
      {/* Selection Control Bar */}
      {selectable && (
        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/80 p-4 rounded-xl border border-slate-800 mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={isAllSelected ? onDeselectAll : onSelectAll}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium transition-colors border border-slate-700"
            >
              {isAllSelected ? <CheckSquare className="w-4 h-4 text-sky-400" /> : <Square className="w-4 h-4" />}
              {isAllSelected ? 'Deselect All' : 'Select All'}
            </button>
            <span className="text-sm font-semibold text-slate-300">
              Selected: <strong className="text-sky-400">{selectedPhotoIds.length}</strong> / {photos.length}
            </span>
          </div>
        </div>
      )}

      {/* Responsive Grid Layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {photos.map((photo, index) => {
          const isSelected = selectedPhotoIds.includes(photo.id);

          return (
            <div
              key={photo.id}
              className={`group relative rounded-xl overflow-hidden glass-card border transition-all duration-200 ${
                isSelected
                  ? 'border-sky-500 ring-2 ring-sky-500/50 scale-[1.02]'
                  : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="aspect-[4/3] bg-slate-950 relative overflow-hidden">
                <img
                  src={photo.url}
                  alt={photo.filename}
                  loading="lazy"
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />

                {/* Selection Overlay */}
                {selectable && (
                  <button
                    onClick={() => onToggleSelectPhoto && onToggleSelectPhoto(photo.id)}
                    className={`absolute top-3 left-3 p-1.5 rounded-lg z-20 transition-all ${
                      isSelected
                        ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/40'
                        : 'bg-slate-950/70 text-slate-300 hover:text-white border border-slate-700'
                    }`}
                  >
                    <Check className="w-4 h-4" />
                  </button>
                )}

                {/* Quick Action Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-between z-10">
                  <div className="flex justify-end gap-2">
                    {onDeletePhoto && (
                      <button
                        onClick={() => onDeletePhoto(photo.id)}
                        className="p-1.5 rounded-lg bg-red-950/80 text-red-300 hover:bg-red-900 border border-red-800/60"
                        title="Delete photo"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => setActivePhotoIndex(index)}
                      className="flex items-center gap-1 text-xs text-slate-200 hover:text-sky-300 font-semibold bg-slate-900/80 px-2.5 py-1 rounded-md border border-slate-700"
                    >
                      <Eye className="w-3.5 h-3.5" /> Preview
                    </button>
                  </div>
                </div>
              </div>

              {/* Card Footer Info */}
              <div className="p-3 bg-slate-900/90 flex items-center justify-between border-t border-slate-800 text-xs">
                <span className="text-slate-300 font-medium truncate pr-2" title={photo.filename}>
                  {photo.filename}
                </span>
                {photo.uploader_name && (
                  <span className="flex items-center gap-1 text-[11px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded border border-slate-700/60 shrink-0">
                    <User className="w-3 h-3 text-sky-400" /> {photo.uploader_name.split(' ')[0]}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox Modal */}
      {activePhotoIndex !== null && (
        <LightboxModal
          photo={photos[activePhotoIndex]}
          onClose={() => setActivePhotoIndex(null)}
          onPrev={() => setActivePhotoIndex((prev) => (prev !== null && prev > 0 ? prev - 1 : prev))}
          onNext={() => setActivePhotoIndex((prev) => (prev !== null && prev < photos.length - 1 ? prev + 1 : prev))}
          hasPrev={activePhotoIndex > 0}
          hasNext={activePhotoIndex < photos.length - 1}
        />
      )}
    </div>
  );
};
