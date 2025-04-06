const CACHE_NAME = 'houtai-cache-v1';
const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000; // 7天缓存过期时间
const STATIC_ASSETS = [
    '/static/css/bootstrap.min.css',
    '/static/css/font-awesome.min.css',
    '/static/css/style.css',
    '/static/css/default.css',
    '/static/js/jquery.min.js',
    '/static/js/bootstrap.bundle.min.js',
    '/static/js/main.js'
];

// 缓存优先级配置
const CACHE_STRATEGIES = {
    // 优先使用缓存的资源
    'CACHE_FIRST': [
        '/static/css/',
        '/static/js/',
        '/static/images/',
        '/static/fonts/'
    ],
    // 优先使用网络的资源
    'NETWORK_FIRST': [
        '/api/',
        '/reports/'
    ]
};

// 安装Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('预缓存静态资源');
                return cache.addAll(STATIC_ASSETS)
                    .catch(error => {
                        console.error('缓存静态资源失败:', error);
                        // 即使部分资源缓存失败，也继续安装
                        return Promise.resolve();
                    });
            })
    );
    
    // 立即激活新的Service Worker
    self.skipWaiting();
});

// 激活Service Worker
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('清除旧缓存:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
        .then(() => {
            console.log('Service Worker已激活');
            // 立即控制所有客户端
            return self.clients.claim();
        })
    );
});

// 确定请求的缓存策略
function getCacheStrategy(url) {
    // API和动态数据用网络优先
    if (CACHE_STRATEGIES.NETWORK_FIRST.some(path => url.includes(path))) {
        return 'NETWORK_FIRST';
    }
    
    // 静态资源用缓存优先
    if (CACHE_STRATEGIES.CACHE_FIRST.some(path => url.includes(path))) {
        return 'CACHE_FIRST';
    }
    
    // 默认网络优先
    return 'NETWORK_FIRST';
}

// 处理资源请求
self.addEventListener('fetch', (event) => {
    // 只处理GET请求
    if (event.request.method !== 'GET') {
        return;
    }
    
    const url = event.request.url;
    const strategy = getCacheStrategy(url);
    
    // 根据不同策略处理请求
    if (strategy === 'CACHE_FIRST') {
        event.respondWith(cacheFirstStrategy(event));
    } else {
        event.respondWith(networkFirstStrategy(event));
    }
});

// 缓存优先策略 - 先尝试从缓存获取，失败则从网络获取
function cacheFirstStrategy(event) {
    return caches.match(event.request)
        .then((cacheResponse) => {
            // 如果有缓存且未过期，直接返回缓存
            if (cacheResponse) {
                // 检查缓存是否过期
                const cachedTime = cacheResponse.headers.get('sw-fetched-on');
                if (cachedTime) {
                    const fetchedTime = parseInt(cachedTime);
                    if (Date.now() - fetchedTime < CACHE_EXPIRATION) {
                        // 缓存未过期，返回缓存
                        return cacheResponse;
                    }
                } else {
                    // 没有时间戳的旧缓存，仍然返回
                    return cacheResponse;
                }
            }
            
            // 缓存不存在或已过期，从网络获取
            return fetchAndCache(event.request);
        })
        .catch(() => {
            // 所有方法都失败，尝试返回默认资源
            return returnDefaultResource(event.request);
        });
}

// 网络优先策略 - 先尝试从网络获取，失败则从缓存获取
function networkFirstStrategy(event) {
    return fetchAndCache(event.request)
        .catch(() => {
            // 网络请求失败，从缓存获取
            return caches.match(event.request)
                .then(cacheResponse => {
                    if (cacheResponse) {
                        return cacheResponse;
                    }
                    
                    // 缓存也没有，尝试返回默认资源
                    return returnDefaultResource(event.request);
                });
        });
}

// 从网络获取并缓存
function fetchAndCache(request) {
    return fetch(request)
        .then(response => {
            // 检查是否有效响应
            if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
            }
            
            // 克隆响应
            const responseToCache = response.clone();
            
            // 添加时间戳头
            const headers = new Headers(responseToCache.headers);
            headers.append('sw-fetched-on', Date.now().toString());
            
            // 创建新的Response对象
            const timestampedResponse = new Response(responseToCache.body, {
                status: responseToCache.status,
                statusText: responseToCache.statusText,
                headers: headers
            });
            
            // 缓存响应
            caches.open(CACHE_NAME)
                .then(cache => {
                    cache.put(request, timestampedResponse);
                });
            
            return response;
        });
}

// 返回默认资源 (如果请求失败)
function returnDefaultResource(request) {
    const url = new URL(request.url);
    
    // 为CSS文件提供默认样式
    if (url.pathname.endsWith('.css')) {
        return caches.match('/static/css/default.css');
    }
    
    // 为JS文件提供空实现
    if (url.pathname.endsWith('.js')) {
        return new Response('// 备用脚本', {
            headers: { 'Content-Type': 'application/javascript' }
        });
    }
    
    // 为图片提供默认图片
    if (url.pathname.match(/\.(jpg|jpeg|png|gif|svg|webp)$/)) {
        // 可以返回一个1x1像素的透明图片
        return new Response(
            new Uint8Array([
                0x47, 0x49, 0x46, 0x38, 0x39, 0x61, 0x01, 0x00, 
                0x01, 0x00, 0x80, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 
                0x00, 0x00, 0x00, 0x21, 0xF9, 0x04, 0x01, 0x00, 
                0x00, 0x00, 0x00, 0x2C, 0x00, 0x00, 0x00, 0x00, 
                0x01, 0x00, 0x01, 0x00, 0x00, 0x02, 0x01, 0x44, 
                0x00, 0x3B
            ]), 
            { headers: { 'Content-Type': 'image/gif' } }
        );
    }
    
    // 默认返回离线页面通知
    return new Response(
        '<html><body><h1>资源暂时无法访问</h1><p>请检查网络连接并刷新页面</p></body></html>',
        { headers: { 'Content-Type': 'text/html' } }
    );
} 