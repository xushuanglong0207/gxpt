/**
 * KnowledgePro - 高级知识库编辑器
 * 集成现代化富文本编辑功能的专业编辑器
 */

// 编辑器实例存储
let editorInstances = {};

// 初始化编辑器
function initKnowledgeEditor(selector, options = {}) {
    console.log('初始化KnowledgePro编辑器:', selector);
    
    // 标准化选择器
    const editorId = selector.replace('#', '');
    const container = document.getElementById(editorId);
    
    if (!container) {
        console.error('找不到编辑器容器:', editorId);
        return null;
    }
    
    // 清理可能存在的旧实例
    destroyEditor(editorId);
    
    // 默认配置
    const defaultOptions = {
        mode: 'edit', // 'edit' 或 'read'
        content: '',
        autosave: true,
        autosaveInterval: 30000, // 30秒
        height: '600px',
        placeholder: '开始编辑您的文档...',
        callbacks: {
            onInit: null,
            onSave: null,
            onChange: null
        }
    };
    
    // 合并用户选项和默认选项
    const mergedOptions = { ...defaultOptions, ...options };
    
    // 创建编辑器DOM结构
    container.innerHTML = '';
    container.className = 'knowledge-pro-editor';
    container.style.height = mergedOptions.height;
    
    // 创建工具栏
    const toolbar = document.createElement('div');
    toolbar.className = 'knowledge-editor-toolbar';
    
    // 工具栏按钮组
    const formatGroup = document.createElement('div');
    formatGroup.className = 'btn-group me-2';
    
    // 文本格式按钮
    const formatButtons = [
        { command: 'bold', icon: 'fa-bold', title: '加粗 (Ctrl+B)' },
        { command: 'italic', icon: 'fa-italic', title: '斜体 (Ctrl+I)' },
        { command: 'underline', icon: 'fa-underline', title: '下划线 (Ctrl+U)' },
        { command: 'strikethrough', icon: 'fa-strikethrough', title: '删除线' }
    ];
    
    formatButtons.forEach(btn => {
        const button = createToolbarButton(btn.icon, btn.title, () => {
            document.execCommand(btn.command, false);
            focusEditor();
        });
        formatGroup.appendChild(button);
    });
    
    // 颜色按钮组
    const colorGroup = document.createElement('div');
    colorGroup.className = 'btn-group me-2';
    
    // 文本颜色按钮
    const textColorButton = createToolbarButton('fa-palette', '文本颜色', () => {
        const colorPicker = document.createElement('input');
        colorPicker.type = 'color';
        colorPicker.value = '#000000';
        colorPicker.style.position = 'absolute';
        colorPicker.style.left = '-9999px';
        document.body.appendChild(colorPicker);
        
        colorPicker.addEventListener('change', () => {
            document.execCommand('foreColor', false, colorPicker.value);
            document.body.removeChild(colorPicker);
            focusEditor();
        });
        
        colorPicker.addEventListener('input', () => {
            document.execCommand('foreColor', false, colorPicker.value);
        });
        
        colorPicker.click();
    });
    
    // 背景色按钮
    const bgColorButton = createToolbarButton('fa-fill-drip', '背景颜色', () => {
        const colorPicker = document.createElement('input');
        colorPicker.type = 'color';
        colorPicker.value = '#ffffff';
        colorPicker.style.position = 'absolute';
        colorPicker.style.left = '-9999px';
        document.body.appendChild(colorPicker);
        
        colorPicker.addEventListener('change', () => {
            document.execCommand('hiliteColor', false, colorPicker.value);
            document.body.removeChild(colorPicker);
            focusEditor();
        });
        
        colorPicker.addEventListener('input', () => {
            document.execCommand('hiliteColor', false, colorPicker.value);
        });
        
        colorPicker.click();
    });
    
    colorGroup.appendChild(textColorButton);
    colorGroup.appendChild(bgColorButton);
    
    // 标题格式按钮组
    const headingGroup = document.createElement('div');
    headingGroup.className = 'btn-group me-2';
    
    const headingButtons = [
        { value: 'h1', text: 'H1', title: '标题1' },
        { value: 'h2', text: 'H2', title: '标题2' },
        { value: 'h3', text: 'H3', title: '标题3' },
        { value: 'p', text: '¶', title: '正文段落' }
    ];
    
    headingButtons.forEach(btn => {
        const button = createToolbarButton(null, btn.title, () => {
            document.execCommand('formatBlock', false, `<${btn.value}>`);
            focusEditor();
        }, btn.text);
        headingGroup.appendChild(button);
    });
    
    // 列表按钮组
    const listGroup = document.createElement('div');
    listGroup.className = 'btn-group me-2';
    
    const listButtons = [
        { command: 'insertUnorderedList', icon: 'fa-list-ul', title: '无序列表' },
        { command: 'insertOrderedList', icon: 'fa-list-ol', title: '有序列表' }
    ];
    
    listButtons.forEach(btn => {
        const button = createToolbarButton(btn.icon, btn.title, () => {
            document.execCommand(btn.command, false);
            focusEditor();
        });
        listGroup.appendChild(button);
    });
    
    // 对齐按钮组
    const alignGroup = document.createElement('div');
    alignGroup.className = 'btn-group me-2';
    
    const alignButtons = [
        { command: 'justifyLeft', icon: 'fa-align-left', title: '左对齐' },
        { command: 'justifyCenter', icon: 'fa-align-center', title: '居中' },
        { command: 'justifyRight', icon: 'fa-align-right', title: '右对齐' },
        { command: 'justifyFull', icon: 'fa-align-justify', title: '两端对齐' }
    ];
    
    alignButtons.forEach(btn => {
        const button = createToolbarButton(btn.icon, btn.title, () => {
            document.execCommand(btn.command, false);
            focusEditor();
        });
        alignGroup.appendChild(button);
    });
    
    // 插入功能按钮组
    const insertGroup = document.createElement('div');
    insertGroup.className = 'btn-group me-2';
    
    const insertButtons = [
        { command: 'createLink', icon: 'fa-link', title: '插入链接' },
        { command: 'unlink', icon: 'fa-unlink', title: '移除链接' },
        { command: 'insertImage', icon: 'fa-image', title: '插入图片' },
        { command: 'insertTable', icon: 'fa-table', title: '插入表格' },
        { command: 'insertHorizontalRule', icon: 'fa-minus', title: '插入分割线' },
        { command: 'code', icon: 'fa-code', title: '插入代码块' }
    ];
    
    insertButtons.forEach(btn => {
        const button = createToolbarButton(btn.icon, btn.title, () => {
            if (btn.command === 'createLink') {
                const url = prompt('请输入链接URL:', 'http://');
                if (url) {
                    document.execCommand('createLink', false, url);
                }
            } else if (btn.command === 'insertImage') {
                const url = prompt('请输入图片URL:', 'http://');
                if (url) {
                    document.execCommand('insertImage', false, url);
                }
            } else if (btn.command === 'insertTable') {
                insertTable();
            } else if (btn.command === 'code') {
                insertCodeBlock();
            } else {
                document.execCommand(btn.command, false);
            }
            focusEditor();
        });
        insertGroup.appendChild(button);
    });
    
    // 编辑功能按钮组
    const editGroup = document.createElement('div');
    editGroup.className = 'btn-group me-2';
    
    const editButtons = [
        { command: 'undo', icon: 'fa-undo', title: '撤销 (Ctrl+Z)' },
        { command: 'redo', icon: 'fa-redo', title: '重做 (Ctrl+Y)' },
        { command: 'removeFormat', icon: 'fa-eraser', title: '清除格式' }
    ];
    
    editButtons.forEach(btn => {
        const button = createToolbarButton(btn.icon, btn.title, () => {
            document.execCommand(btn.command, false);
            focusEditor();
        });
        editGroup.appendChild(button);
    });
    
    // 将所有按钮组添加到工具栏
    toolbar.appendChild(formatGroup);
    toolbar.appendChild(colorGroup);
    toolbar.appendChild(headingGroup);
    toolbar.appendChild(listGroup);
    toolbar.appendChild(alignGroup);
    toolbar.appendChild(insertGroup);
    toolbar.appendChild(editGroup);
    
    // 创建内容编辑区域
    const contentArea = document.createElement('div');
    contentArea.className = 'knowledge-editor-content';
    contentArea.contentEditable = mergedOptions.mode === 'edit';
    contentArea.innerHTML = mergedOptions.content || `<p>${mergedOptions.placeholder}</p>`;
    
    // 附加DOM结构
    container.appendChild(toolbar);
    container.appendChild(contentArea);
    
    // 设置只读模式样式
    if (mergedOptions.mode === 'read') {
        toolbar.style.display = 'none';
        contentArea.style.border = '1px solid #eee';
        contentArea.style.backgroundColor = '#f9f9f9';
    }
    
    // 添加内容变化事件监听
    let changeTimeout = null;
    contentArea.addEventListener('input', () => {
        if (mergedOptions.callbacks.onChange) {
            clearTimeout(changeTimeout);
            changeTimeout = setTimeout(() => {
                mergedOptions.callbacks.onChange(contentArea.innerHTML);
            }, 300);
        }
        
        // 自动保存
        if (mergedOptions.autosave && typeof window.saveArticle === 'function') {
            clearTimeout(editorInstances[editorId].autosaveTimeout);
            editorInstances[editorId].autosaveTimeout = setTimeout(() => {
                console.log('自动保存文档...');
                window.saveArticle();
            }, mergedOptions.autosaveInterval);
        }
    });
    
    // 添加快捷键支持
    contentArea.addEventListener('keydown', e => {
        // Ctrl+S 保存
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            if (typeof window.saveArticle === 'function') {
                window.saveArticle();
            }
        }
        // 其他常用快捷键不需要处理，浏览器内置支持
    });
    
    // 创建编辑器API
    const editorAPI = {
        getContent: () => contentArea.innerHTML,
        setContent: (html) => {
            contentArea.innerHTML = html || '';
            return editorAPI;
        },
        getMode: () => mergedOptions.mode,
        setMode: (mode) => {
            contentArea.contentEditable = mode === 'edit';
            toolbar.style.display = mode === 'edit' ? 'flex' : 'none';
            if (mode === 'read') {
                contentArea.style.border = '1px solid #eee';
                contentArea.style.backgroundColor = '#f9f9f9';
            } else {
                contentArea.style.border = '1px solid #ced4da';
                contentArea.style.backgroundColor = '#fff';
            }
            mergedOptions.mode = mode;
            return editorAPI;
        },
        focus: () => {
            contentArea.focus();
            // 将光标移到内容末尾
            const range = document.createRange();
            const sel = window.getSelection();
            range.selectNodeContents(contentArea);
            range.collapse(false);
            sel.removeAllRanges();
            sel.addRange(range);
            return editorAPI;
        },
        destroy: () => {
            container.innerHTML = '';
            delete editorInstances[editorId];
        },
        autosaveTimeout: null
    };
    
    // 存储编辑器实例
    editorInstances[editorId] = editorAPI;
    
    // 触发初始化回调
    if (mergedOptions.callbacks.onInit) {
        mergedOptions.callbacks.onInit(editorAPI);
    }
    
    return editorAPI;
}

// 销毁编辑器
function destroyEditor(selector) {
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    
    if (editorInstances[editorId]) {
        clearTimeout(editorInstances[editorId].autosaveTimeout);
        editorInstances[editorId].destroy();
        return true;
    }
    
    return false;
}

// 获取编辑器实例
function getEditor(selector) {
    const editorId = typeof selector === 'string' ? selector.replace('#', '') : selector;
    return editorInstances[editorId] || null;
}

// 辅助函数：创建工具栏按钮
function createToolbarButton(iconClass, title, onClick, text) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn btn-outline-secondary btn-sm';
    button.title = title;
    
    if (iconClass) {
        const icon = document.createElement('i');
        icon.className = `fas ${iconClass}`;
        button.appendChild(icon);
    } else if (text) {
        button.textContent = text;
    }
    
    button.addEventListener('click', onClick);
    return button;
}

// 辅助函数：聚焦编辑器
function focusEditor() {
    setTimeout(() => {
        const activeEditor = document.querySelector('.knowledge-editor-content[contenteditable=true]');
        if (activeEditor) {
            activeEditor.focus();
        }
    }, 10);
}

// 辅助函数：插入表格
function insertTable() {
    const rows = prompt('请输入表格行数:', '3');
    const cols = prompt('请输入表格列数:', '3');
    
    if (!rows || !cols) return;
    
    const numRows = parseInt(rows, 10);
    const numCols = parseInt(cols, 10);
    
    if (isNaN(numRows) || isNaN(numCols) || numRows < 1 || numCols < 1) {
        alert('请输入有效的行数和列数');
        return;
    }
    
    let tableHtml = '<table class="table table-bordered"><tbody>';
    
    // 创建表头
    tableHtml += '<tr>';
    for (let j = 0; j < numCols; j++) {
        tableHtml += '<th>表头 ' + (j + 1) + '</th>';
    }
    tableHtml += '</tr>';
    
    // 创建表格内容
    for (let i = 0; i < numRows; i++) {
        tableHtml += '<tr>';
        for (let j = 0; j < numCols; j++) {
            tableHtml += '<td>单元格 ' + (i + 1) + '-' + (j + 1) + '</td>';
        }
        tableHtml += '</tr>';
    }
    
    tableHtml += '</tbody></table><p></p>';
    
    document.execCommand('insertHTML', false, tableHtml);
}

// 辅助函数：插入代码块
function insertCodeBlock() {
    const language = prompt('请输入代码语言 (如 javascript, python, css 等):', 'javascript');
    
    if (language === null) return;
    
    const codeBlockHtml = `
    <pre><code class="language-${language}">// 在此处输入代码
    </code></pre><p></p>
    `;
    
    document.execCommand('insertHTML', false, codeBlockHtml);
}

// 导出编辑器API
window.KnowledgePro = {
    init: initKnowledgeEditor,
    destroy: destroyEditor,
    get: getEditor
}; 