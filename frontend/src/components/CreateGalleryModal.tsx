import React, { useState } from 'react';
import { Lock, Sparkles } from 'lucide-react';
import { Modal } from './Modal';
import { api } from '../services/api';
import type { Gallery } from '../types';

interface CreateGalleryModalProps {
  isOpen: boolean;
  onClose: () => void;
  eventId: string;
  selectedPhotoIds: string[];
  onGalleryCreated: (gallery: Gallery) => void;
}

export const CreateGalleryModal: React.FC<CreateGalleryModalProps> = ({
  isOpen,
  onClose,
  eventId,
  selectedPhotoIds,
  onGalleryCreated,
}) => {
  const [name, setName] = useState('');
  const [pin, setPin] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError('Gallery name is required');
      return;
    }
    if (!pin || pin.length < 4 || pin.length > 8) {
      setError('PIN must be 4 to 8 digits long');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const res = await api.post('/galleries', {
        event_id: eventId,
        name: name.trim(),
        pin: pin.trim(),
        photo_ids: selectedPhotoIds,
      });

      const pubRes = await api.post(`/galleries/${res.data.id}/publish`);
      onGalleryCreated(pubRes.data);
      onClose();
      setName('');
      setPin('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create gallery');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Customer Gallery">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-1">Gallery Title</label>
          <input
            type="text"
            placeholder="e.g. Official Highlights Gallery"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-1 flex items-center justify-between">
            <span>Secure Gallery PIN (4 - 8 Digits)</span>
            <span className="text-xs text-sky-400 font-normal flex items-center gap-1">
              <Lock className="w-3 h-3" /> Hashed Security
            </span>
          </label>
          <input
            type="text"
            placeholder="e.g. 123456"
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, '').slice(0, 8))}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm tracking-widest font-mono"
            required
          />
          <p className="text-xs text-slate-400 mt-1">This PIN will be required by customers to unlock the published gallery.</p>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between text-xs text-slate-300">
          <span>Selected Photos for Gallery:</span>
          <strong className="text-sky-400 font-bold">{selectedPhotoIds.length} photos</strong>
        </div>

        {error && (
          <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-red-300 text-xs">
            {error}
          </div>
        )}

        <div className="pt-3 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold text-sm shadow-lg shadow-sky-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4" /> {isLoading ? 'Publishing...' : 'Create & Publish Gallery'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
