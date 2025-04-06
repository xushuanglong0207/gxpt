/**
 * 自定义编辑器配置
 * 简单、可靠的编辑器解决方案
 */

// 全局变量记录编辑器实例
let editorInstances = {};

// 初始化编辑器
function initTinyMCE(selector, options = {}) {
    // 去掉选择器的#号
    const editorId = selector.replace('#', '');
    
    // 获取编辑器容器
    const container = document.getElementById(editorId);
    if (!container) {
        console.error('找不到编辑器容器:', editorId);
        return;
    }
    
    // 销毁已存在的编辑器
    destroyTinyMCE(editorId);
    
    // 清空容器
    container.innerHTML = '';
    container.style.padding = '0';
    container.style.overflow = 'hidden';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.height = '100%';
    
    // 创建工具栏
    const toolbar = document.createElement('div');
    toolbar.className = 'custom-editor-toolbar';
    toolbar.style.display = options.readonly ? 'none' : 'flex';
    toolbar.innerHTML = `
        <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="bold" title="加粗"><i class="fas fa-bold"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="italic" title="斜体"><i class="fas fa-italic"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="underline" title="下划线"><i class="fas fa-underline"></i></button>
        </div>
        <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="formatBlock" data-value="h1" title="标题1">H1</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="formatBlock" data-value="h2" title="标题2">H2</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="formatBlock" data-value="h3" title="标题3">H3</button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="formatBlock" data-value="p" title="段落">P</button>
        </div>
        <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertUnorderedList" title="无序列表"><i class="fas fa-list-ul"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertOrderedList" title="有序列表"><i class="fas fa-list-ol"></i></button>
        </div>
        <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="createLink" title="插入链接"><i class="fas fa-link"></i></button>
            <button type="button" class="btn btn-sm btn-outline-secondary" data-command="insertImage" title="插入图片"><i class="fas fa-image"></i></button>
        </div>
    `;
    
    // 创建内容区域
    const contentArea = document.createElement('div');
    contentArea.className = 'custom-editor-content';
    contentArea.setAttribute('contenteditable', !options.readonly);
    contentArea.style.cssText = `
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 1rem;
        min-height: 400px;
        height: calc(100% - 50px);
        overflow-y: auto;
        background-color: white;
        outline: none;
        font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
        font-size: 16px;
        line-height: 1.6;
    `;

    // 添加提示
    if (!options.readonly && (!options.setup || typeof options.setup !== 'function')) {
        contentArea.innerHTML = '<p>点击这里开始编辑</p>';
    }
    
    // 创建编辑器对象
    const editorObj = {
        setContent: function(html) {
            contentArea.innerHTML = html || '';
            return this;
        },
        getContent: function() {
            return contentArea.innerHTML;
        },
        mode: {
            set: function(mode) {
                const isReadOnly = mode === 'readonly';
                contentArea.setAttribute('contenteditable', !isReadOnly);
                toolbar.style.display = isReadOnly ? 'none' : 'flex';
                // 更新样式
                if (isReadOnly) {
                    contentArea.style.border = '1px solid transparent';
                    contentArea.style.backgroundColor = '#f8f9fa';
                } else {
                    contentArea.style.border = '1px solid #dee2e6';
                    contentArea.style.backgroundColor = 'white';
                }
            }
        }
    };
    
    // 保存实例
    editorInstances[editorId] = editorObj;
    
    // 设置内容区域初始内容
    if (options.setup && typeof options.setup === 'function') {
        // 调用设置函数
        options.setup(editorObj);
    }
    
    // 添加CSS
    const styleId = 'custom-editor-style';
    if (!document.getElementById(styleId)) {
        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .custom-editor-toolbar {
                display: flex;
                flex-wrap: wrap;
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 0.25rem;
                margin-bottom: 8px;
            }
            .custom-editor-toolbar button {
                margin-right: 2px;
            }
            .custom-editor-content {
                margin-bottom: 10px;
            }
        `;
        document.head.appendChild(style);
    }
    
    // 添加工具栏事件处理
    toolbar.addEventListener('click', function(e) {
        const button = e.target.closest('button');
        if (!button) return;
        
        const command = button.getAttribute('data-command');
        if (!command) return;
        
        e.preventDefault();
        
        if (command === 'createLink') {
            const url = prompt('请输入链接URL:', 'http://');
            if (url) {
                document.execCommand('createLink', false, url);
            }
        } else if (command === 'insertImage') {
            const url = prompt('请输入图片URL:', 'http://');
            if (url) {
                document.execCommand('insertImage', false, url);
            }
        } else if (command === 'formatBlock') {
            const value = button.getAttribute('data-value');
            document.execCommand('formatBlock', false, value);
        } else {
            document.execCommand(command, false, null);
        }
    });
    
    // 清除默认提示
    contentArea.addEventListener('focus', function() {
        if (contentArea.innerHTML === '<p>点击这里开始编辑</p>') {
            contentArea.innerHTML = '';
        }
    });
    
    // 组装编辑器
    container.appendChild(toolbar);
    container.appendChild(contentArea);
    
    // 初始化只读模式
    if (options.readonly) {
        contentArea.setAttribute('contenteditable', 'false');
        contentArea.style.border = '1px solid transparent';
        contentArea.style.backgroundColor = '#f8f9fa';
        toolbar.style.display = 'none';
    } else {
        // 非只读模式下，自动聚焦
        setTimeout(() => {
            contentArea.focus();
        }, 100);
    }
    
    console.log('编辑器初始化完成，模式:', options.readonly ? '只读' : '编辑');
    
    // 返回API对象
    return editorObj;
}

// 销毁编辑器实例
function destroyTinyMCE(selector) {
    // 去掉选择器的#号
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    
    // 清除保存的实例
    if (editorInstances[editorId]) {
        delete editorInstances[editorId];
    }
    
    // 清空容器
    const container = document.getElementById(editorId);
    if (container) {
        container.innerHTML = '';
    }
    
    return true;
}

// 获取编辑器内容
function getTinyMCEContent(selector) {
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    
    // 从实例获取内容
    if (editorInstances[editorId]) {
        return editorInstances[editorId].getContent();
    }
    
    // 或直接从DOM获取
    const container = document.getElementById(editorId);
    const contentArea = container?.querySelector('.custom-editor-content');
    return contentArea ? contentArea.innerHTML : '';
}

// 设置编辑器内容
function setTinyMCEContent(selector, content) {
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    
    // 从实例设置内容
    if (editorInstances[editorId]) {
        editorInstances[editorId].setContent(content);
        return true;
    }
    
    // 或直接通过DOM设置
    const container = document.getElementById(editorId);
    const contentArea = container?.querySelector('.custom-editor-content');
    if (contentArea) {
        contentArea.innerHTML = content || '';
        return true;
    }
    
    return false;
}

// 设置编辑器是否只读
function setTinyMCEReadOnly(selector, readOnly) {
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    
    if (editorInstances[editorId]) {
        editorInstances[editorId].mode.set(readOnly ? 'readonly' : 'design');
        return true;
    }
    
    return false;
} 