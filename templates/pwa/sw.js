{% load static %}
/* Nations Flow — Service Worker (offline mínimo)
   Estratégias:
   - Navegação: network-first com fallback para página offline
   - Estáticos: network-first com fallback para cache (evita servir assets
     antigos por causa do stale-while-revalidate + nginx expires 1y)
   - API/autenticação: network-only (nunca cachear)

   IMPORTANTE: ao alterar estáticos, incremente VERSION para forçar a
   limpeza do cache antigo nos clientes (o activate só apaga chaves != VERSION). */
const VERSION = 'nationsflow-v2';
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

    // Requisições cross-origin (CDNs: jquery/bootstrap/select2) não são
    // interceptadas: o fetch do SW é regido pelo connect-src da CSP, que não
    // inclui os CDNs. Deixá-las passar mantém o carregamento direto pelo
    // navegador e evita o ERR_FAILED que derrubava o jQuery na página.
    const requestUrl = new URL(event.request.url);
    if (requestUrl.origin !== self.location.origin) return;

    // Navegação: network-first com fallback offline
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request, { cache: 'no-cache' })
                .then((response) => {
                    const copy = response.clone();
                    caches.open(VERSION).then((cache) => cache.put(event.request, copy));
                    return response;
                })
                .catch(() => caches.match(event.request).then((cached) => cached || caches.match(OFFLINE_URL)))
        );
        return;
    }

    // Estáticos: network-first com fallback para cache
    // (stale-while-revalidate servia assets antigos; network-first garante
    //  sempre a versão nova quando há conexão. `cache: 'no-cache'` força a
    //  revalidação com o servidor em vez de usar o cache HTTP immutable do nginx)
    event.respondWith(
        fetch(event.request, { cache: 'no-cache' })
            .then((response) => {
                if (response && response.status === 200 && response.type === 'basic') {
                    const copy = response.clone();
                    caches.open(VERSION).then((cache) => cache.put(event.request, copy));
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
