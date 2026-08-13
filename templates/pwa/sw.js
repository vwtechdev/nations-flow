{% load static %}
/* Nations Flow — Service Worker (offline mínimo)
   Estratégias:
   - Navegação: network-first com fallback para página offline
   - Estáticos: stale-while-revalidate
   - API/autenticação: network-only (nunca cachear) */
const VERSION = 'nationsflow-v1';
const OFFLINE_URL = '{% static "offline.html" %}';

const PRECACHE_ASSETS = [
    '{% static "css/base.css" %}',
    '{% static "css/responsive_tables.css" %}',
    '{% static "js/index.js" %}',
    '{% static "js/filters_form.js" %}',
    '{% static "js/transaction_list.js" %}',
    '{% static "js/login.js" %}',
    '{% static "img/icon.svg" %}',
    OFFLINE_URL,
];

function isApiRequest(request) {
    const url = new URL(request.url);
    return request.method !== 'GET' ||
        url.pathname.includes('/api/') ||
        url.pathname.includes('transactions/api/');
}

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(VERSION).then((cache) => cache.addAll(PRECACHE_ASSETS)).then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(keys.filter((key) => key !== VERSION).map((key) => caches.delete(key)))
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    if (isApiRequest(event.request)) return;

    // Navegação: network-first com fallback offline
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    const copy = response.clone();
                    caches.open(VERSION).then((cache) => cache.put(event.request, copy));
                    return response;
                })
                .catch(() => caches.match(event.request).then((cached) => cached || caches.match(OFFLINE_URL)))
        );
        return;
    }

    // Estáticos: stale-while-revalidate
    event.respondWith(
        caches.match(event.request).then((cached) => {
            const fetchPromise = fetch(event.request).then((response) => {
                if (response && response.status === 200 && response.type === 'basic') {
                    const copy = response.clone();
                    caches.open(VERSION).then((cache) => cache.put(event.request, copy));
                }
                return response;
            }).catch(() => cached);
            return cached || fetchPromise;
        })
    );
});
