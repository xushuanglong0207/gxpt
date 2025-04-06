/* PrismJS 1.24.1 - 简化版 */
(function(){
    var Prism = {
        languages: {},
        highlightAll: function() {
            var elements = document.querySelectorAll('code[class*="language-"], [class*="language-"] code, code[class*="lang-"], [class*="lang-"] code');
            for (var i=0, element; element = elements[i++];) {
                Prism.highlightElement(element);
            }
        },
        highlightElement: function(element) {
            // 简单实现，仅标记代码块
            element.className += ' prism-highlighted';
        }
    };

    // 在页面加载后执行高亮
    if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', Prism.highlightAll);
    }

    // 暴露到全局
    window.Prism = Prism;
})(); 