// 定义编辑器类
class WangEditor {
    constructor(options = {}) {
        this.options = {
            selector: '#editor-container',
            toolbarSelector: '#toolbar-container',
            height: '500px',
            placeholder: '请输入内容...',
            readOnly: false,
            ...options
        };
        
        this.container = document.querySelector(this.options.selector);
        this.toolbarContainer = document.querySelector(this.options.toolbarSelector);
        
        if (!this.container || !this.toolbarContainer) {
            throw new Error('找不到编辑器容器或工具栏容器');
        }
        
        this.init();
    }
    
    // 初始化编辑器
    init() {
        // 设置容器样式
        this.container.style.height = this.options.height;
        this.container.contentEditable = !this.options.readOnly;
        this.container.className = 'w-e-text-container';
        
        // 创建工具栏
        this.createToolbar();
        
        // 设置占位符
        if (this.options.placeholder && !this.options.readOnly) {
            this.container.setAttribute('placeholder', this.options.placeholder);
        }
        
        // 绑定事件
        this.bindEvents();
    }
    
    // 创建工具栏
    createToolbar() {
        if (this.options.readOnly) {
            this.toolbarContainer.style.display = 'none';
            return;
        }
        
        this.toolbarContainer.className = 'w-e-toolbar';
        
        const tools = [
            { name: '段落', command: 'formatBlock', value: 'p' },
            { name: '标题1', command: 'formatBlock', value: 'h1' },
            { name: '标题2', command: 'formatBlock', value: 'h2' },
            { name: '标题3', command: 'formatBlock', value: 'h3' },
            { type: 'divider' },
            { name: '粗体', command: 'bold' },
            { name: '斜体', command: 'italic' },
            { name: '下划线', command: 'underline' },
            { type: 'divider' },
            { name: '引用', command: 'formatBlock', value: 'blockquote' },
            { name: '有序列表', command: 'insertOrderedList' },
            { name: '无序列表', command: 'insertUnorderedList' },
            { type: 'divider' },
            { name: '左对齐', command: 'justifyLeft' },
            { name: '居中', command: 'justifyCenter' },
            { name: '右对齐', command: 'justifyRight' },
            { type: 'divider' },
            { name: '插入链接', command: 'createLink' },
            { name: '插入图片', command: 'insertImage' },
            { name: '插入表格', command: 'insertTable' },
            { name: '代码块', command: 'formatBlock', value: 'pre' },
            { type: 'divider' },
            { name: '撤销', command: 'undo' },
            { name: '重做', command: 'redo' }
        ];
        
        tools.forEach(tool => {
            if (tool.type === 'divider') {
                const divider = document.createElement('span');
                divider.className = 'w-e-bar-divider';
                this.toolbarContainer.appendChild(divider);
            } else {
                const button = document.createElement('button');
                button.className = 'w-e-bar-item';
                button.textContent = tool.name;
                button.onclick = () => this.execCommand(tool);
                this.toolbarContainer.appendChild(button);
            }
        });
    }
    
    // 执行命令
    execCommand(tool) {
        try {
            if (tool.command === 'createLink') {
                const url = prompt('请输入链接地址:', 'https://');
                if (url) {
                    document.execCommand(tool.command, false, url);
                }
            } else if (tool.command === 'insertImage') {
                const url = prompt('请输入图片地址:', 'https://');
                if (url) {
                    document.execCommand(tool.command, false, url);
                }
            } else if (tool.command === 'insertTable') {
                const rows = prompt('请输入行数:', '3');
                const cols = prompt('请输入列数:', '3');
                if (rows && cols) {
                    let tableHtml = '<table border="1" style="width:100%;border-collapse:collapse;">';
                    for (let i = 0; i < parseInt(rows); i++) {
                        tableHtml += '<tr>';
                        for (let j = 0; j < parseInt(cols); j++) {
                            tableHtml += '<td style="padding:5px;border:1px solid #ddd;">&nbsp;</td>';
                        }
                        tableHtml += '</tr>';
                    }
                    tableHtml += '</table>';
                    document.execCommand('insertHTML', false, tableHtml);
                }
            } else if (tool.value) {
                document.execCommand(tool.command, false, tool.value);
            } else {
                document.execCommand(tool.command, false, null);
            }
            
            // 保持焦点
            this.container.focus();
        } catch (error) {
            console.error('执行命令失败:', error);
        }
    }
    
    // 绑定事件
    bindEvents() {
        // 处理粘贴事件
        this.container.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = e.clipboardData.getData('text/plain');
            document.execCommand('insertText', false, text);
        });
        
        // 处理拖放事件
        this.container.addEventListener('drop', (e) => {
            e.preventDefault();
        });
        
        // 处理输入事件
        this.container.addEventListener('input', () => {
            if (typeof this.options.onChange === 'function') {
                this.options.onChange(this);
            }
        });
    }
    
    // 获取HTML内容
    getHtml() {
        return this.container.innerHTML;
    }
    
    // 设置HTML内容
    setHtml(html) {
        this.container.innerHTML = html || '';
    }
    
    // 获取纯文本内容
    getText() {
        return this.container.innerText;
    }
    
    // 聚焦
    focus() {
        this.container.focus();
    }
    
    // 失焦
    blur() {
        this.container.blur();
    }
    
    // 销毁编辑器
    destroy() {
        // 移除事件监听
        this.container.removeEventListener('paste');
        this.container.removeEventListener('drop');
        this.container.removeEventListener('input');
        
        // 清空内容
        this.container.innerHTML = '';
        this.toolbarContainer.innerHTML = '';
        
        // 移除属性
        this.container.removeAttribute('contenteditable');
        this.container.removeAttribute('placeholder');
        this.container.className = '';
        this.toolbarContainer.className = '';
    }
}

// 导出编辑器对象
window.wangEditor = {
    createEditor: function(options) {
        return new WangEditor(options);
    },
    createToolbar: function(options) {
        // 工具栏已在编辑器初始化时创建，这里返回一个空对象保持API兼容
        return {};
    }
}; 