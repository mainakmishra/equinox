// api/profileApi.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchUserProfileByEmail(email: string) {
  const res = await fetch(`${API_URL}/profile/user?email=${encodeURIComponent(email)}`);
  if (!res.ok) throw new Error('Failed to fetch user profile');
  return res.json();
}
