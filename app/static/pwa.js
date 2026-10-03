// Registers the service worker (served from the site root so it covers every page)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js', { scope: '/' })
            .catch(err => console.log('SW failed', err));
    });
}