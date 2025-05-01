import api from './apiService';

export const registerUser = async (formData) => {
  const response = await api.post('/register', formData);
  return response.data;
};

export const loginUser = async (email, password) => {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  try {
    const response = await api.post('/token', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });

    const { access_token } = response.data;
    localStorage.setItem('token', access_token);
    window.dispatchEvent(new Event('storage'));
    return access_token;
  } catch (error) {
    console.error('Login error:', error.response?.data || error.message);
    throw error;
  }
};

export const getCurrentUser = async () => {
  try {
    const response = await api.get('/users/me');
    return response.data; // `{ username, email }`
  } catch (error) {
    console.error('Error fetching user:', error.response?.data || error.message);
    logoutUser();
    return null;
  }
};

export const logoutUser = () => {
  localStorage.removeItem('token');
  window.dispatchEvent(new Event('storage'));
};
