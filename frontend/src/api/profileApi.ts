// api/profileApi.ts

export async function fetchUserProfileByEmail(email: string) {
  const res = await fetch(`http://localhost:8000/profile/user?email=${encodeURIComponent(email)}`);
  if (!res.ok) throw new Error('Failed to fetch user profile');
  return res.json();
}
