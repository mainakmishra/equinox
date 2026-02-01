// api/authApi.ts

export async function handleGoogleSignIn() {
  try {
    const res = await fetch("http://localhost:8000/auth/google/login");
    const data = await res.json();
    if (data.auth_url) {
      window.location.href = data.auth_url;
    }
  } catch (err) {
    // Optionally handle error
    console.error("Google sign-in failed", err);
  }
}
