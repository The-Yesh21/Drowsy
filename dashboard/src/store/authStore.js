import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      driver: null,
      isAuthenticated: false,

      login: (token, driver) => set({
        token,
        driver,
        isAuthenticated: true,
      }),

      logout: () => set({
        token: null,
        driver: null,
        isAuthenticated: false,
      }),

      updateDriver: (updatedDriver) => set((state) => ({
        driver: { ...state.driver, ...updatedDriver },
      })),
    }),
    {
      name: 'drowsiness-auth-storage', // Key in localStorage
    }
  )
);
