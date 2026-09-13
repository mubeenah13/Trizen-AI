import React, { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { Modal } from './Modal';
import { api } from '../services/api';
import type { EventMember } from '../types';

interface AssignMemberModalProps {
  isOpen: boolean;
  onClose: () => void;
  eventId: string;
  onMemberAssigned: (member: EventMember) => void;
}

export const AssignMemberModal: React.FC<AssignMemberModalProps> = ({
  isOpen,
  onClose,
  eventId,
  onMemberAssigned,
}) => {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const regRes = await api.post('/auth/register', {
        name: email.split('@')[0],
        email: email.trim().toLowerCase(),
        password: 'TeamPassword123!',
        role: 'TEAM_MEMBER',
      }).catch((err) => {
        if (err.response?.status === 409) return null;
        throw err;
      });

      let userId = regRes?.data?.user?.id;

      if (!userId) {
        setError('User already exists. Enter exact user ID or create new team member email.');
        setIsLoading(false);
        return;
      }

      const res = await api.post(`/events/${eventId}/members`, { user_id: userId });
      onMemberAssigned(res.data);
      onClose();
      setEmail('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to assign team member');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Team Member to Event">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-slate-300 mb-1">Team Member Email</label>
          <input
            type="email"
            placeholder="e.g. photographer@trizen.ai"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 text-sm"
            required
          />
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
            className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-semibold text-sm shadow-lg shadow-emerald-500/20 disabled:opacity-50 flex items-center gap-2"
          >
            <UserPlus className="w-4 h-4" /> {isLoading ? 'Assigning...' : 'Assign Team Member'}
          </button>
        </div>
      </form>
    </Modal>
  );
};
