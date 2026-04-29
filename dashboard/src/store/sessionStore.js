import { create } from 'zustand';

// Store for managing the currently active driving session explicitly
export const useSessionStore = create((set) => ({
  activeSessionId: null,

  setActiveSession: (id) => set({ activeSessionId: id }),
  clearActiveSession: () => set({ activeSessionId: null }),
}));
