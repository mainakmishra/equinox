// api/authApi.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function handleGoogleSignIn() {
  try {
    const res = await fetch(`${API_URL}/auth/google/login`);
    const data = await res.json();
    if (data.auth_url) {
      window.location.href = data.auth_url;
    }
  } catch (err) {
    console.error("Google sign-in failed", err);
  }
}
