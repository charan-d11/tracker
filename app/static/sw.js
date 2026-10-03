// const CACHE_NAME = 'pot-tracker-v1';
// const urlsToCache = [
//     '/',
//     '/static/style.css',
//     '/static/manifest.json'
// ];

// self.addEventListener('install', event => {
//     event.waitUntil(
//         caches.open(CACHE_NAME)
//             .then(cache => cache.addAll(urlsToCache))
//     );
// });

// self.addEventListener('fetch', event => {
//     event.respondWith(
//         caches.match(event.request)
//             .then(response => response || fetch(event.request))
//     );
// });

// Service worker for Shared Pot Tracker
// Rule: only public static files are cached. Pages and /api/* data are never
// stored, so one person's data can't show up for another user on a shared device.

const CACHE = 'pot-static-v1';

const PRECACHE = [
  '/static/style.css',
  '/static/offline.html',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(PRECACHE))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Page loads: always go to the network (login state matters).
  // If offline, show a simple offline page.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => caches.match('/static/offline.html'))
    );
    return;
  }

  // Static files: serve from cache, refresh in the background.
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(req).then(cached => {
          const fresh = fetch(req).then(res => {
            if (res.ok) cache.put(req, res.clone());
            return res;
          }).catch(() => cached);
          return cached || fresh;
        })
      )
    );
  }
  // Everything else (/api/..., etc.) goes straight to the network, uncached.
});