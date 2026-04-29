import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Activity } from 'lucide-react';

import apiClient from '../api/client';
import { useAuthStore } from '../store/authStore';

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const loginAction = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isLogin) {
        // Form URL Encoded for OAuth2 Password Bearer
        const params = new URLSearchParams();
        params.append('username', formData.email);
        params.append('password', formData.password);
        
        const res = await apiClient.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        loginAction(res.data.access_token, { id: res.data.driver_id, email: formData.email });
        
        // Fetch full profile
        const profileRes = await apiClient.get('/auth/me', {
            headers: { Authorization: `Bearer ${res.data.access_token}` }
        });
        useAuthStore.getState().updateDriver(profileRes.data);
        
        toast.success("Logged in successfully");
        navigate('/dashboard');
        
      } else {
        // Register JSON payload
        const payload = {
            name: formData.name,
            email: formData.email,
            password: formData.password
        };
        
        const res = await apiClient.post('/auth/register', payload);
        loginAction(res.data.access_token, { id: res.data.driver_id, email: formData.email });
        
        const profileRes = await apiClient.get('/auth/me', {
            headers: { Authorization: `Bearer ${res.data.access_token}` }
        });
        useAuthStore.getState().updateDriver(profileRes.data);
        
        toast.success("Account created successfully");
        navigate('/dashboard');
      }
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.detail || "Authentication failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-800 rounded-xl shadow-2xl overflow-hidden border border-slate-700">
        <div className="p-8">
          <div className="flex justify-center mb-8">
            <div className="flex items-center gap-2">
              <Activity className="h-10 w-10 text-blue-500" />
              <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">
                SafeDrive
              </span>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-white text-center mb-8">
            {isLogin ? "Sign in to Dashboard" : "Create Driver Account"}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input 
                  type="text" 
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                  placeholder="John Doe"
                />
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
              <input 
                type="email" 
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                placeholder="driver@example.com"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Password</label>
              <input 
                type="password" 
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                placeholder="Min 6 characters"
              />
            </div>
            
            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-800 transition-all disabled:opacity-50"
            >
              {isLoading ? "Processing..." : (isLogin ? "Sign In" : "Register")}
            </button>
          </form>
          
          <div className="mt-6 text-center">
            <button 
              onClick={() => setIsLogin(!isLogin)}
              className="text-slate-400 hover:text-white transition-colors text-sm"
            >
              {isLogin ? "Need an account? Register here" : "Already have an account? Sign in"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
