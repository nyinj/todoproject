document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  const err = document.getElementById('loginError');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    err.innerText = '';
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    try {
      const res = await fetch('/api/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) {
        const txt = await res.text();
        err.innerText = 'Login failed';
        console.error('login failed', txt);
        return;
      }
      const data = await res.json();
      localStorage.setItem('access_token', data.access);
      localStorage.setItem('refresh_token', data.refresh);
      // redirect to app
      window.location.href = '/';
    } catch (error) {
      console.error(error);
      err.innerText = 'An error occurred';
    }
  });
});