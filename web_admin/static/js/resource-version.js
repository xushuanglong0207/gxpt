// 资源版本配置
const RESOURCE_VERSIONS = {
    'css/bootstrap.min.css': '5.1.3',
    'css/font-awesome.min.css': '5.15.3',
    'css/style.css': '1.0.0',
    'js/jquery.min.js': '3.6.0',
    'js/bootstrap.bundle.min.js': '5.1.3',
    'js/main.js': '1.0.0'
};

// 获取资源版本号
function getResourceVersion(path) {
    return RESOURCE_VERSIONS[path] || '1.0.0';
}

// 添加版本号到URL
function addVersionToUrl(url) {
    const path = url.split('/static/')[1];
    const version = getResourceVersion(path);
    return `${url}?v=${version}`;
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getResourceVersion,
        addVersionToUrl
    };
} 