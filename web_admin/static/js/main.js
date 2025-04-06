/**
 * 自动化测试平台前端脚本
 * 作者: longshen
 * 修改: 修复页面显示问题
 */

// 页面加载完成后执行
$(document).ready(function() {
    console.log("页面加载完成，初始化UI...");
    
    // 初始化工具提示
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // 初始化弹出框
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // 确保toastr已初始化 - 移除自动测试
    if (typeof toastr === 'undefined') {
        console.error("找不到toastr库！检查是否正确加载了toastr.js");
    }
    
    // 页面加载完成后显示动画效果
    // 修复：使用setTimeout延迟显示，确保DOM已完全渲染
    setTimeout(function() {
        $('.fade-in').css('opacity', 1);
        // 确保内容区域可见
        $('#main-content').css('display', 'block').css('opacity', 1);
    }, 100);
    
    // 为卡片添加悬停效果
    $('.card').hover(
        function() {
            $(this).addClass('card-hover');
        },
        function() {
            $(this).removeClass('card-hover');
        }
    );
    
    // 表单提交前验证
    $('form').on('submit', function(e) {
        var requiredFields = $(this).find('[required]');
        var valid = true;
        
        requiredFields.each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                valid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!valid) {
            e.preventDefault();
            showToast('请填写所有必填字段', 'warning');
        }
    });
    
    // 添加动漫人物角色助手
    if ($('.dashboard-container').length) {
        addAnimeHelper();
    }
    
    // 确认删除对话框
    $('.delete-confirm').on('click', function(e) {
        e.preventDefault();
        var form = $(this).closest('form');
        
        if (confirm('确定要删除吗？此操作不可撤销。')) {
            form.submit();
        }
    });
    
    // 修复: 确保导航切换正常工作
    $('.nav-link').on('click', function(e) {
        const href = $(this).attr('href');
        
        // 如果链接为空或者是#，则阻止默认行为
        if (!href || href === '#') {
            e.preventDefault();
            // 已移除详细调试输出
        }
    });
    
    // 修复: 确保页面内容区域正确显示
    $('#main-content').show();
    
    // 初始化页面淡入效果 - 简化此函数避免冲突
    simplifiedFadeInElements();
    
    // 任务创建页面 - 模块选择
    $('#module-select').on('change', function() {
        var selectedModules = $(this).val();
        var submoduleContainer = $('#submodule-container');
        submoduleContainer.empty();
        
        if (selectedModules && selectedModules.length > 0) {
            selectedModules.forEach(function(module) {
                var submoduleSelect = $('<div class="mb-3">' +
                    '<label class="form-label">'+module+'子模块</label>' +
                    '<select class="form-select" name="submodules" id="submodule-'+module+'">' +
                    '<option value="">选择子模块</option>' +
                    '</select>' +
                    '</div>');
                
                submoduleContainer.append(submoduleSelect);
                
                // 从后端获取子模块，而不是使用硬编码的值
                loadSubmodulesFromServer(module, '#submodule-'+module);
            });
        }
    });
    
    // 从服务器加载子模块选项
    function loadSubmodulesFromServer(module, selectId) {
        var submoduleSelect = $(selectId);
        
        // 显示加载状态
        submoduleSelect.html('<option value="">正在加载...</option>');
        
        // 从服务器获取子模块列表
        $.ajax({
            url: '/api/modules/' + module + '/submodules',
            type: 'GET',
            success: function(data) {
                submoduleSelect.empty();
                submoduleSelect.append('<option value="">选择子模块</option>');
                
                // 添加从服务器获取的子模块
                if (data && data.length > 0) {
                    data.forEach(function(submodule) {
                        submoduleSelect.append('<option value="' + submodule.value + '">' + submodule.name + '</option>');
                    });
                } else {
                    submoduleSelect.append('<option value="" disabled>没有可用的子模块</option>');
                }
            },
            error: function() {
                submoduleSelect.html('<option value="">加载失败，请重试</option>');
            }
        });
    }
    
    // 任务状态实时更新
    function updateTaskStatus() {
        $('.task-status').each(function() {
            var statusBadge = $(this);
            var taskId = statusBadge.data('task-id');
            
            if (statusBadge.hasClass('status-running')) {
                $.get('/tasks/' + taskId + '/status', function(data) {
                    if (data.status !== 'running') {
                        statusBadge.removeClass('status-running').addClass('status-' + data.status);
                        statusBadge.text(data.status);
                        
                        // 如果任务完成，刷新页面
                        if (data.status === 'completed' || data.status === 'failed') {
                            setTimeout(function() {
                                location.reload();
                            }, 2000);
                        }
                    }
                });
            }
        });
    }
    
    // 如果页面上有正在运行的任务，每5秒更新一次状态
    if ($('.status-running').length > 0) {
        setInterval(updateTaskStatus, 5000);
    }
    
    // 报告过滤功能
    $('#report-filter').on('input', function() {
        var filterValue = $(this).val().toLowerCase();
        
        $('.report-item').each(function() {
            var reportName = $(this).data('report-name').toLowerCase();
            var reportType = $(this).data('report-type').toLowerCase();
            
            if (reportName.includes(filterValue) || reportType.includes(filterValue)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // 任务过滤功能
    $('#task-filter').on('input', function() {
        var filterValue = $(this).val().toLowerCase();
        
        $('.task-item').each(function() {
            var taskName = $(this).data('task-name').toLowerCase();
            var taskModules = $(this).data('task-modules').toLowerCase();
            var taskStatus = $(this).data('task-status').toLowerCase();
            
            if (taskName.includes(filterValue) || 
                taskModules.includes(filterValue) || 
                taskStatus.includes(filterValue)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // 任务状态颜色和图标更新
    $('.task-status').each(function() {
        updateTaskStatusDisplay($(this));
    });
    
    // 登录页面动画效果
    if ($('.login-container').length || $('.register-container').length) {
        animateLoginElements();
        addSakuraEffect();
    }
    
    // 处理表单提交时的加载动画
    $('form').on('submit', function() {
        // 检查是否是创建/运行任务的表单
        if ($(this).attr('action') && 
            ($(this).attr('action').includes('/tasks/create') || 
             $(this).attr('action').includes('/tasks/run'))) {
            
            // 显示加载动画
            showLoading('任务正在处理中，请稍候...');
            
            // 设置超时，如果30秒后仍未完成，显示提示
            setTimeout(function() {
                updateLoadingMessage('任务处理时间较长，请继续等待...');
            }, 30000);
            
            // 如果90秒后仍未完成，提供选项
            setTimeout(function() {
                updateLoadingMessage('任务可能需要较长时间执行，您可以返回任务列表页面查看状态');
                showReturnButton();
            }, 90000);
        }
    });
    
    // 防止任何报告预览页面的加载
    preventReportPreview();
    
    // 初始化任务创建页面 - 确保必须有运行命令
    initTaskCreateForm();
    
    // 初始化任务编辑页面
    initTaskEditPage();
});

// 简化的淡入效果初始化
function simplifiedFadeInElements() {
    $('.fade-enter').addClass('fade-enter-active');
}

// 添加樱花飘落效果
function addSakuraEffect() {
    var sakuraColors = [
        'rgba(255, 183, 197, 0.9)',
        'rgba(255, 197, 208, 0.9)',
        'rgba(255, 209, 220, 0.9)',
        'rgba(255, 221, 228, 0.9)'
    ];
    
    var sakuraContainer = $('<div class="sakura-container"></div>');
    $('body').prepend(sakuraContainer);
    
    // 创建樱花
    for (var i = 0; i < 15; i++) {
        createSakura(sakuraContainer, sakuraColors);
    }
    
    // 持续创建樱花
    setInterval(function() {
        createSakura(sakuraContainer, sakuraColors);
    }, 1000);
}

// 创建单个樱花
function createSakura(container, colors) {
    var size = Math.random() * 15 + 10;
    var color = colors[Math.floor(Math.random() * colors.length)];
    var left = Math.random() * 100;
    var animationDuration = Math.random() * 10 + 10;
    var delay = Math.random() * 5;
    
    var sakura = $(`<div class="sakura" style="
        width: ${size}px;
        height: ${size}px;
        left: ${left}%;
        background-color: ${color};
        animation-duration: ${animationDuration}s;
        animation-delay: ${delay}s;
    "></div>`);
    
    container.append(sakura);
    
    // 动画完成后删除元素
    setTimeout(function() {
        sakura.remove();
    }, (animationDuration + delay) * 1000);
}

// 登录页面的特殊动画
function animateLoginElements() {
    $('.login-card').addClass('animated');
    
    // 自动聚焦到用户名输入框
    $('#username').focus();
    
    // 添加小动漫角色
    var animeCharacter = $('<div class="anime-character login-character"></div>');
    $('.login-container').append(animeCharacter);
    
    // 输入框交互效果
    $('.form-control').on('focus', function() {
        animeCharacter.addClass('excited');
    }).on('blur', function() {
        animeCharacter.removeClass('excited');
    });
}

// 添加动漫助手角色
function addAnimeHelper() {
    var helperHtml = `
        <div class="anime-helper">
            <div class="anime-character dashboard-character"></div>
            <div class="speech-bubble">
                <p>欢迎回来！需要帮助吗？</p>
                <div class="helper-actions">
                    <button class="btn btn-sm btn-outline-primary helper-btn" data-action="create-task">
                        <i class="fas fa-plus-circle"></i> 创建任务
                    </button>
                    <button class="btn btn-sm btn-outline-primary helper-btn" data-action="view-reports">
                        <i class="fas fa-chart-bar"></i> 查看报告
                    </button>
                    <button class="btn btn-sm btn-outline-secondary helper-dismiss">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(helperHtml);
    
    // 显示助手
    setTimeout(function() {
        $('.anime-helper').addClass('show');
    }, 1000);
    
    // 助手按钮点击事件
    $('.helper-btn').on('click', function() {
        var action = $(this).data('action');
        
        // 隐藏助手
        $('.anime-helper').removeClass('show');
        
        // 执行相应动作
        if (action === 'create-task') {
            window.location.href = '/tasks/create';
        } else if (action === 'view-reports') {
            window.location.href = '/reports';
        }
    });
    
    // 关闭助手
    $('.helper-dismiss').on('click', function() {
        $('.anime-helper').removeClass('show');
        localStorage.setItem('helper_dismissed', 'true');
    });
}

// 确认对话框
function showConfirmDialog(title, message, confirmCallback) {
    // 移除任何现有的对话框
    $('.confirm-dialog-container').remove();
    
    var dialogHtml = `
        <div class="confirm-dialog-container">
            <div class="confirm-dialog-overlay"></div>
            <div class="confirm-dialog">
                <div class="confirm-dialog-header">
                    <h5>${title}</h5>
                    <button class="btn-close dialog-close"></button>
                </div>
                <div class="confirm-dialog-body">
                    <p>${message}</p>
                </div>
                <div class="confirm-dialog-footer">
                    <button class="btn btn-secondary dialog-close">取消</button>
                    <button class="btn btn-danger dialog-confirm">确认</button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(dialogHtml);
    
    // 显示对话框
    setTimeout(function() {
        $('.confirm-dialog').addClass('show');
        $('.confirm-dialog-overlay').addClass('show');
    }, 10);
    
    // 关闭对话框
    $('.dialog-close').on('click', function() {
        closeConfirmDialog();
    });
    
    // 确认操作
    $('.dialog-confirm').on('click', function() {
        closeConfirmDialog();
        if (typeof confirmCallback === 'function') {
            confirmCallback();
        }
    });
}

// 关闭确认对话框
function closeConfirmDialog() {
    $('.confirm-dialog').removeClass('show');
    $('.confirm-dialog-overlay').removeClass('show');
    
    setTimeout(function() {
        $('.confirm-dialog-container').remove();
    }, 300);
}

// 更新任务状态显示
function updateTaskStatusDisplay(element) {
    var status = element.text().trim();
    
    // 根据状态设置图标
    var icon = '';
    if (status === 'pending') {
        icon = '<i class="fas fa-clock me-1"></i>';
    } else if (status === 'running') {
        icon = '<i class="fas fa-spinner fa-spin me-1"></i>';
    } else if (status === 'completed') {
        icon = '<i class="fas fa-check-circle me-1"></i>';
    } else if (status === 'failed') {
        icon = '<i class="fas fa-times-circle me-1"></i>';
    }
    
    // 更新文本
    if (icon) {
        element.html(icon + status);
    }
}

// 检测是否为移动设备
function isMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// 动画元素初始化
function initFadeInElements() {
    $('.fade-in').each(function(index) {
        var element = $(this);
        setTimeout(function() {
            element.addClass('show');
        }, 100 * index);
    });
}

// 显示加载提示
function showLoading(message) {
    // 如果不存在加载层，则创建
    if ($('#loading-container').length === 0) {
        var loadingHtml = '<div id="loading-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 9999; display: flex; align-items: center; justify-content: center;">' +
            '<div class="bg-white p-4 rounded shadow-sm text-center" style="max-width: 80%;">' +
            '<div class="spinner-border text-primary mb-3" role="status">' +
            '<span class="visually-hidden">Loading...</span>' +
            '</div>' +
            '<p id="loading-message" class="mb-3">' + message + '</p>' +
            '<div id="loading-actions" class="d-none">' +
            '<a href="/tasks" class="btn btn-outline-secondary btn-sm">返回任务列表</a>' +
            '</div>' +
            '</div>' +
            '</div>';
            
        $('body').append(loadingHtml);
    } else {
        // 更新消息
        $('#loading-message').text(message);
    }
}

// 更新加载消息
function updateLoadingMessage(message) {
    $('#loading-message').text(message);
}

// 显示返回按钮
function showReturnButton() {
    $('#loading-actions').removeClass('d-none');
}

// 隐藏加载提示
function hideLoading() {
    $('#loading-container').remove();
}

// 防止报告预览页面加载，直接跳转到HTML报告
function preventReportPreview() {
    // 拦截所有指向报告预览页面的链接
    $(document).on('click', 'a[href*="/reports/"]', function(e) {
        var href = $(this).attr('href');
        
        // 如果是报告预览页面链接，则阻止默认行为
        if (href && href.match(/\/reports\/[^\/]+$/)) {
            e.preventDefault();
            
            // 提取报告ID
            var reportId = href.split('/').pop();
            
            // 直接跳转到HTML报告文件
            openReportHtml(reportId);
            return false;
        }
    });
    
    // 处理"查看报告"按钮点击
    $(document).on('click', '.view-report-btn, [data-action="view-report"]', function(e) {
        e.preventDefault();
        
        // 获取报告ID或路径
        var reportId = $(this).data('report-id');
        var reportPath = $(this).data('report-path');
        
        if (reportPath) {
            // 如果提供了完整路径，直接打开
            window.open(reportPath, '_blank');
        } else if (reportId) {
            // 如果只提供了ID，构建路径并打开
            openReportHtml(reportId);
        } else {
            showToast('无法找到报告文件', 'warning');
        }
        
        return false;
    });
}

// 打开HTML报告文件
function openReportHtml(reportId) {
    // 尝试直接打开静态HTML文件
    var reportUrl = '/reports/' + (reportId.endsWith('.html') ? reportId : reportId + '.html');
    
    // 在新标签页中打开
    window.open(reportUrl, '_blank');
}

// 添加任务编辑功能
$(document).on('click', '.edit-task-btn', function(e) {
    e.preventDefault();
    var taskId = $(this).data('task-id');
    
    if (taskId) {
        window.location.href = '/tasks/edit/' + taskId;
    } else {
        showToast('无法找到任务ID', 'warning');
    }
});

// 初始化任务编辑页面
function initTaskEditPage() {
    if ($('#task-edit-form').length > 0) {
        // 加载任务数据
        var taskId = $('#task-edit-form').data('task-id');
        
        // 加载并填充当前任务信息
        $.ajax({
            url: '/api/tasks/' + taskId,
            type: 'GET',
            success: function(taskData) {
                // 填充表单
                $('#task-name').val(taskData.name);
                $('#task-description').val(taskData.description);
                
                // 设置模块和子模块
                if (taskData.modules) {
                    $('#module-select').val(taskData.modules).trigger('change');
                    
                    // 在子模块加载完成后设置子模块值
                    setTimeout(function() {
                        if (taskData.submodules) {
                            taskData.modules.forEach(function(module, index) {
                                $('#submodule-' + module).val(taskData.submodules[index]);
                            });
                        }
                    }, 1000); // 延迟设置子模块值以确保子模块已加载
                }
                
                // 设置其他任务相关字段
                if (taskData.priority) {
                    $('#task-priority').val(taskData.priority);
                }
                
                // 初始化表单验证
                initFormValidation('#task-edit-form');
            },
            error: function() {
                showToast('加载任务信息失败', 'danger');
            }
        });
        
        // 监听表单提交
        $('#task-edit-form').on('submit', function(e) {
            e.preventDefault();
            
            // 检查表单验证
            if (!$(this)[0].checkValidity()) {
                e.stopPropagation();
                $(this).addClass('was-validated');
                return;
            }
            
            // 收集表单数据
            var formData = $(this).serialize();
            
            // 提交更新
            $.ajax({
                url: '/api/tasks/' + taskId,
                type: 'PUT',
                data: formData,
                success: function(response) {
                    showToast('任务更新成功', 'success');
                    // 更新成功后，重定向到任务列表页
                    setTimeout(function() {
                        window.location.href = '/tasks';
                    }, 1500);
                },
                error: function() {
                    showToast('任务更新失败，请重试', 'danger');
                }
            });
        });
    }
}

// 表单验证初始化
function initFormValidation(formSelector) {
    $(formSelector).addClass('needs-validation');
    $(formSelector).find('input[required], select[required], textarea[required]').each(function() {
        $(this).on('blur', function() {
            if (!this.checkValidity()) {
                $(this).addClass('is-invalid');
            } else {
                $(this).removeClass('is-invalid');
            }
        });
    });
}

// 初始化任务创建表单
function initTaskCreateForm() {
    if ($('#task-create-form').length > 0) {
        // 强制添加运行命令字段
        addRunCommandField();
        
        // 表单提交前验证
        $('#task-create-form').on('submit', function(e) {
            if (!$('#run-command').val()) {
                e.preventDefault();
                showToast('必须指定运行命令', 'warning');
                $('#run-command').addClass('is-invalid');
                $('#run-command').focus();
                return false;
            }
        });
    }
}

// 添加运行命令字段
function addRunCommandField() {
    // 如果已经存在，则不添加
    if ($('#run-command').length > 0) {
        return;
    }
    
    var commandHTML = `
        <div class="mb-3" id="run-command-container">
            <label for="run-command" class="form-label"><span class="text-danger">*</span> 运行命令</label>
            <input type="text" class="form-control" id="run-command" name="run_command" 
                placeholder="例如: python run_test.py --module api" required>
            <div class="form-text text-danger">必须指定测试执行的具体命令，否则将导致任务无法正常完成</div>
        </div>
    `;
    
    // 添加到表单的最后一个分组之前
    $('#task-create-form .btn-primary').parent().before(commandHTML);
}

// 简化的资源加载器
var SimpleResourceLoader = {
    loadScript: function(url, callback) {
        console.log("加载脚本:", url);
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = url;
        script.onload = callback || function() {};
        document.head.appendChild(script);
    },
    
    loadStyle: function(url, callback) {
        console.log("加载样式:", url);
        var link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onload = callback || function() {};
        document.head.appendChild(link);
    }
};

// 为后续代码提供简化的接口
window.SimpleResourceLoader = SimpleResourceLoader;

// 性能监控
const PerformanceMonitor = {
    metrics: {
        resourceTiming: [],
        errors: [],
        warnings: []
    },

    init() {
        this.observeResourceTiming();
        this.observeErrors();
        this.observeMemory();
    },

    observeResourceTiming() {
        const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            entries.forEach(entry => {
                if (entry.duration > 200) {
                    console.warn('慢资源:', entry.name, '加载时间:', entry.duration.toFixed(2), 'ms');
                    this.metrics.warnings.push({
                        type: 'slow-resource',
                        resource: entry.name,
                        duration: entry.duration
                    });
                }
                this.metrics.resourceTiming.push(entry);
            });
        });
        
        observer.observe({ entryTypes: ['resource'] });
    },

    observeErrors() {
        window.addEventListener('error', (event) => {
            this.metrics.errors.push({
                message: event.message,
                source: event.filename,
                line: event.lineno,
                column: event.colno,
                timestamp: Date.now()
            });
            console.error('页面错误:', event.message);
        });
    },

    observeMemory() {
        if (window.performance && performance.memory) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > memory.jsHeapSizeLimit * 0.9) {
                    console.warn('内存使用接近限制:', 
                        (memory.usedJSHeapSize / 1024 / 1024).toFixed(2), 'MB/',
                        (memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2), 'MB');
                }
            }, 30000);
        }
    },

    getMetrics() {
        return this.metrics;
    }
};

// DOM 操作优化
const DOMOptimizer = {
    // 缓存频繁访问的DOM元素
    cache: new Map(),

    // 获取元素（带缓存）
    get(selector) {
        if (!this.cache.has(selector)) {
            this.cache.set(selector, document.querySelector(selector));
        }
        return this.cache.get(selector);
    },

    // 批量更新DOM
    batchUpdate(updates) {
        const fragment = document.createDocumentFragment();
        updates.forEach(update => {
            const element = document.createElement(update.tag);
            Object.assign(element, update.properties);
            if (update.attributes) {
                Object.entries(update.attributes).forEach(([key, value]) => {
                    element.setAttribute(key, value);
                });
            }
            if (update.content) {
                element.textContent = update.content;
            }
            fragment.appendChild(element);
        });
        return fragment;
    },

    // 防抖动画帧
    debounceFrame(callback) {
        let frameId = null;
        return (...args) => {
            if (frameId) {
                cancelAnimationFrame(frameId);
            }
            frameId = requestAnimationFrame(() => {
                callback(...args);
                frameId = null;
            });
        };
    },

    // 清理缓存
    clearCache() {
        this.cache.clear();
    }
};

// 事件优化
const EventOptimizer = {
    handlers: new Map(),

    // 添加防抖动事件处理器
    addDebouncedHandler(element, eventType, handler, delay = 250) {
        let timeoutId;
        const debouncedHandler = (event) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => handler(event), delay);
        };
        
        element.addEventListener(eventType, debouncedHandler);
        this.handlers.set(handler, debouncedHandler);
        
        return () => {
            element.removeEventListener(eventType, debouncedHandler);
            this.handlers.delete(handler);
        };
    },

    // 添加节流事件处理器
    addThrottledHandler(element, eventType, handler, limit = 250) {
        let inThrottle;
        const throttledHandler = (event) => {
            if (!inThrottle) {
                handler(event);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
        
        element.addEventListener(eventType, throttledHandler);
        this.handlers.set(handler, throttledHandler);
        
        return () => {
            element.removeEventListener(eventType, throttledHandler);
            this.handlers.delete(handler);
        };
    },

    // 使用事件委托
    delegate(element, eventType, selector, handler) {
        const delegatedHandler = (event) => {
            const target = event.target.closest(selector);
            if (target && element.contains(target)) {
                handler.call(target, event);
            }
        };
        
        element.addEventListener(eventType, delegatedHandler);
        this.handlers.set(handler, delegatedHandler);
        
        return () => {
            element.removeEventListener(eventType, delegatedHandler);
            this.handlers.delete(handler);
        };
    }
};

// 初始化性能监控
document.addEventListener('DOMContentLoaded', () => {
    // 初始化性能监控
    PerformanceMonitor.init();
    
    // 优化滚动事件
    EventOptimizer.addThrottledHandler(window, 'scroll', () => {
        // 处理滚动相关的UI更新
    }, 16); // 约60fps
    
    // 优化窗口调整事件
    EventOptimizer.addDebouncedHandler(window, 'resize', () => {
        // 处理窗口大小改变后的UI更新
    }, 250);
    
    // 使用事件委托处理动态元素
    EventOptimizer.delegate(document.body, 'click', '[data-action]', (event) => {
        const action = event.target.dataset.action;
        if (typeof window[action] === 'function') {
            window[action](event);
        }
    });
});

// 导出工具
window.ResourceLoader = SimpleResourceLoader;
window.PerformanceMonitor = PerformanceMonitor;
window.DOMOptimizer = DOMOptimizer;
window.EventOptimizer = EventOptimizer;

// 主应用脚本
document.addEventListener('DOMContentLoaded', function() {
    
    // 处理移动端下拉菜单问题
    initMobileDropdowns();
    
    // 初始化所有提示框
    initTooltips();
    
    // 初始化所有弹出框
    initPopovers();
});

// 初始化移动端下拉菜单
function initMobileDropdowns() {
    // 修复移动端下拉菜单问题
    if (window.innerWidth < 992) {
        // 找到所有下拉菜单切换按钮
        const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
        
        dropdownToggles.forEach(toggle => {
            // 移除原始的Bootstrap事件
            toggle.setAttribute('data-bs-toggle', '');
            
            // 添加自定义点击处理
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // 获取下拉菜单
                const dropdown = this.nextElementSibling;
                
                // 切换显示状态
                if (dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                    dropdown.style.display = 'none';
                    this.setAttribute('aria-expanded', 'false');
                } else {
                    // 先关闭所有其他打开的下拉菜单
                    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                        menu.classList.remove('show');
                        menu.style.display = 'none';
                        menu.previousElementSibling.setAttribute('aria-expanded', 'false');
                    });
                    
                    // 打开当前下拉菜单
                    dropdown.classList.add('show');
                    dropdown.style.display = 'block';
                    this.setAttribute('aria-expanded', 'true');
                }
            });
        });
        
        // 点击页面其他区域关闭下拉菜单
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                    menu.style.display = 'none';
                    menu.previousElementSibling.setAttribute('aria-expanded', 'false');
                });
            }
        });
    }
}

// 初始化提示框
function initTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化弹出框
function initPopovers() {
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// 检测浏览器是否支持某些功能
function checkBrowserSupport() {
    // 检测Intersection Observer API支持
    if (!('IntersectionObserver' in window)) {
        console.log('浏览器不支持IntersectionObserver API');
    }
    
    // 检测WebP支持
    var webpTest = new Image();
    webpTest.onload = function() {
        var isWebpSupported = (webpTest.width > 0) && (webpTest.height > 0);
        document.documentElement.classList.add(isWebpSupported ? 'webp' : 'no-webp');
    };
    webpTest.onerror = function() {
        document.documentElement.classList.add('no-webp');
    };
    webpTest.src = 'data:image/webp;base64,UklGRhoAAABXRUJQVlA4TA0AAAAvAAAAEAcQERGIiP4HAA==';
}

// 延迟加载图片
function lazyLoadImages() {
    if ('IntersectionObserver' in window) {
        const imgObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    const src = img.getAttribute('data-src');
                    
                    if (src) {
                        img.setAttribute('src', src);
                        img.removeAttribute('data-src');
                        img.classList.add('loaded');
                    }
                    
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imgObserver.observe(img);
        });
    } else {
        // 回退策略：立即加载所有图片
        document.querySelectorAll('img[data-src]').forEach(img => {
            const src = img.getAttribute('data-src');
            if (src) {
                img.setAttribute('src', src);
                img.removeAttribute('data-src');
            }
        });
    }
}

// 全局标志，防止重复初始化
window.userDropdownFixed = false;

// 修复用户下拉菜单
function fixUserDropdown() {
    console.log('开始修复用户下拉菜单...');
    
    // 强制删除所有可能存在的菜单
    document.querySelectorAll('.user-dropdown-menu').forEach(menu => {
        menu.remove();
        console.log('删除已存在的菜单');
    });
    
    // 获取用户按钮
    const userButton = document.getElementById('userButton');
    if (!userButton) {
        console.log('找不到用户按钮，无法初始化下拉菜单');
        return;
    }
    
    console.log('找到用户按钮:', userButton);
    
    // 设置点击事件（使用闭包避免全局变量）
    userButton.onclick = (function() {
        // 在闭包中创建菜单元素
        let dropdownMenu = null;
        let isMenuVisible = false;
        
        // 创建一个新的菜单元素
        function createMenu() {
            // 创建菜单元素
            const menu = document.createElement('div');
            menu.className = 'user-dropdown-menu';
            menu.id = 'userDropdownMenu';
            menu.style.position = 'absolute';
            menu.style.backgroundColor = '#ffffff';
            menu.style.border = '1px solid #cccccc';
            menu.style.borderRadius = '4px';
            menu.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            menu.style.padding = '8px 0';
            menu.style.zIndex = '999999';
            menu.style.minWidth = '180px';
            menu.style.display = 'none';
            
            // 添加菜单项
            menu.innerHTML = `
                <a class="dropdown-item" href="/edit_profile">
                    <i class="fas fa-user me-2"></i>个人信息
                </a>
                <a class="dropdown-item" href="/edit_profile">
                    <i class="fas fa-cog me-2"></i>设置
                </a>
                <div class="dropdown-divider"></div>
                <a class="dropdown-item" href="/logout">
                    <i class="fas fa-sign-out-alt me-2"></i>退出登录
                </a>
            `;
            
            // 为菜单项添加样式
            const style = document.createElement('style');
            style.textContent = `
                .user-dropdown-menu .dropdown-item {
                    display: block;
                    padding: 8px 16px;
                    text-decoration: none;
                    color: #333;
                    font-size: 14px;
                }
                
                .user-dropdown-menu .dropdown-item:hover {
                    background-color: #f8f9fa;
                }
                
                .user-dropdown-menu .dropdown-item i {
                    margin-right: 8px;
                    width: 16px;
                    text-align: center;
                }
                
                .user-dropdown-menu .dropdown-divider {
                    height: 1px;
                    margin: 8px 0;
                    background-color: #e9ecef;
                }
            `;
            
            menu.appendChild(style);
            return menu;
        }
        
        // 点击处理函数
        return function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('用户按钮被点击');
            
            // 第一次点击时创建菜单
            if (!dropdownMenu) {
                dropdownMenu = createMenu();
                document.body.appendChild(dropdownMenu);
                console.log('创建新的下拉菜单');
                
                // 添加全局点击事件来关闭菜单
                document.addEventListener('click', function closeMenu(e) {
                    if (isMenuVisible && !dropdownMenu.contains(e.target) && e.target !== userButton) {
                        console.log('检测到外部点击，关闭菜单');
                        dropdownMenu.style.display = 'none';
                        isMenuVisible = false;
                    }
                });
            }
            
            // 切换菜单可见性
            if (!isMenuVisible) {
                // 计算位置 - 在按钮下方
                const buttonRect = userButton.getBoundingClientRect();
                const menuWidth = 180; // 假设菜单宽度
                
                // 基于按钮位置计算
                const topPosition = buttonRect.bottom + window.scrollY;
                const leftPosition = Math.max(0, buttonRect.right - menuWidth + window.scrollX);
                
                console.log('显示菜单，位置:', {top: topPosition, left: leftPosition});
                
                // 设置位置
                dropdownMenu.style.top = topPosition + 'px';
                dropdownMenu.style.left = leftPosition + 'px';
                dropdownMenu.style.display = 'block';
                isMenuVisible = true;
            } else {
                console.log('隐藏菜单');
                dropdownMenu.style.display = 'none';
                isMenuVisible = false;
            }
        };
    })();
    
    console.log('用户下拉菜单初始化完成');
}

// 在DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM加载完成，等待100ms后初始化下拉菜单...');
    setTimeout(fixUserDropdown, 100);
});

/* 自定义消息处理函数 - 高级版 */
function showCustomFlash(message, category) {
  if (!message) return;
  
  // 创建alert元素
  const alertWrapper = document.createElement('div');
  alertWrapper.className = 'alert-wrapper';
  
  // 主容器
  const alertElement = document.createElement('div');
  alertElement.className = `custom-alert alert-${category}`;
  alertElement.setAttribute('role', 'alert');
  
  // 图标部分
  const iconDiv = document.createElement('div');
  iconDiv.className = 'alert-icon';
  
  const icon = document.createElement('i');
  if (category === 'success') {
    icon.className = 'fas fa-check-circle';
  } else if (category === 'danger') {
    icon.className = 'fas fa-exclamation-circle';
  } else if (category === 'warning') {
    icon.className = 'fas fa-exclamation-triangle';
  } else {
    icon.className = 'fas fa-info-circle';
  }
  iconDiv.appendChild(icon);
  
  // 内容部分
  const contentDiv = document.createElement('div');
  contentDiv.className = 'alert-content';
  contentDiv.textContent = message;
  
  // 关闭按钮
  const closeBtn = document.createElement('button');
  closeBtn.className = 'close-btn';
  closeBtn.innerHTML = '&times;';
  closeBtn.onclick = function() {
    closeAlert(alertElement);
  };
  
  // 进度条
  const progressDiv = document.createElement('div');
  progressDiv.className = 'alert-progress';
  
  // 组装alert
  alertElement.appendChild(iconDiv);
  alertElement.appendChild(contentDiv);
  alertElement.appendChild(closeBtn);
  alertElement.appendChild(progressDiv);
  
  alertWrapper.appendChild(alertElement);
  
  // 添加到容器
  const container = document.getElementById('customFlashContainer');
  if (container) {
    container.appendChild(alertWrapper);
  }
  
  // 启动自动淡出
  setTimeout(() => {
    closeAlert(alertElement);
  }, 5000); // 5秒后自动关闭
  
  // 返回创建的元素，方便测试
  return alertElement;
}

/* 关闭提示框的函数 */
function closeAlert(alertElement) {
  if (!alertElement) return;
  
  // 添加关闭动画类
  alertElement.classList.add('alert-closing');
  
  // 动画结束后移除元素
  setTimeout(() => {
    const wrapper = alertElement.closest('.alert-wrapper');
    if (wrapper && wrapper.parentNode) {
      wrapper.parentNode.removeChild(wrapper);
    }
  }, 500); // 与动画时长相同
}

// 增强版页面加载检测 - 确保flash消息在所有页面都能正确显示
document.addEventListener('DOMContentLoaded', function() {
  console.log("页面加载完成，检查flash消息...");
  
  // 直接检查页面上的flash消息容器
  const flashContainer = document.getElementById('flash-container');
  if (flashContainer) {
    console.log("找到flash容器，确保消息可见");
    // 确保消息可见并添加自动消失计时器
    const alerts = flashContainer.querySelectorAll('.alert');
    if (alerts.length > 0) {
      console.log("发现" + alerts.length + "条消息");
      alerts.forEach(function(alert) {
        // 确保警告显示出来
        alert.style.display = 'block';
        alert.style.opacity = '1';
        
        // 5秒后自动淡出
        setTimeout(function() {
          alert.classList.add('fade-out');
          setTimeout(function() {
            alert.remove();
          }, 500);
        }, 5000);
      });
    } else {
      console.log("没有找到flash消息，尝试从referrer获取");
      // 如果没有通过flash找到消息，尝试通过referrer检测
      checkReferrerForMessages();
    }
  } else {
    console.log("未找到flash容器，尝试从referrer获取");
    // 如果没有flash容器，也尝试通过referrer检测
    checkReferrerForMessages();
  }
  
  // 在login页面监听表单提交
  const loginForm = document.querySelector('form');
  if (loginForm && window.location.pathname.includes('/login')) {
    loginForm.addEventListener('submit', function() {
      console.log("登录表单提交，设置会话标记");
      sessionStorage.setItem('formSubmitted', 'true');
    });
  }
});

// 检查referrer来显示适当的消息
function checkReferrerForMessages() {
  const currentPath = window.location.pathname;
  const referrer = document.referrer;
  console.log("当前路径:", currentPath, "来源:", referrer);
  
  if (currentPath === '/' || currentPath.includes('/index')) {
    // 首页 - 检查是否从登录页面来
    if (referrer.includes('/login')) {
      console.log("从登录页面到首页，显示登录成功消息");
      // 直接使用toastr显示登录成功消息
      if (typeof toastr !== 'undefined') {
        console.log("使用toastr显示登录成功消息");
        toastr.success('登录成功！');
      } else if (typeof showToast === 'function') {
        console.log("使用showToast显示登录成功消息");
        showToast('登录成功！', 'success');
      } else {
        console.log("toastr和showToast都不可用，使用标准alert");
        showStandardAlert('登录成功！', 'success');
      }
    }
  } else if (currentPath.includes('/login')) {
    // 登录页面 - 检查是否从登出页面来
    if (referrer.includes('/logout')) {
      console.log("从登出页面到登录页，显示登出成功消息");
      if (typeof toastr !== 'undefined') {
        toastr.success('已退出登录！');
      } else {
        showStandardAlert('已退出登录！', 'success');
      }
    }
    
    // 检查是否登录失败
    const hasSubmittedBefore = sessionStorage.getItem('formSubmitted');
    if (hasSubmittedBefore === 'true') {
      console.log("检测到之前提交过表单，可能是登录失败");
      if (typeof toastr !== 'undefined') {
        toastr.error('用户名或密码错误！');
      } else {
        showStandardAlert('用户名或密码错误！', 'danger');
      }
      sessionStorage.removeItem('formSubmitted');
    }
  }
}

// 标准alert显示函数 - 适用于任何页面
function showStandardAlert(message, category) {
  console.log("显示标准alert:", message, category);
  
  // 尝试找到或创建flash容器
  let container = document.getElementById('flash-container');
  if (!container) {
    // 在login页面
    container = document.querySelector('.login-container');
    if (container) {
      const flashDiv = document.createElement('div');
      flashDiv.id = 'flash-container';
      container.insertBefore(flashDiv, container.firstChild);
      container = flashDiv;
    } else {
      // 其他页面
      const mainContent = document.querySelector('.container') || document.body;
      const flashDiv = document.createElement('div');
      flashDiv.id = 'flash-container';
      flashDiv.style.margin = '20px 0';
      mainContent.insertBefore(flashDiv, mainContent.firstChild);
      container = flashDiv;
    }
  }
  
  // 创建alert元素
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert alert-${category} alert-dismissible fade show`;
  alertDiv.role = 'alert';
  alertDiv.style.animation = 'fadeIn 0.5s';
  
  // 添加图标
  let icon = document.createElement('i');
  if (category === 'success') {
    icon.className = 'fas fa-check-circle me-1';
  } else if (category === 'danger') {
    icon.className = 'fas fa-exclamation-circle me-1';
  } else if (category === 'warning') {
    icon.className = 'fas fa-exclamation-triangle me-1';
  } else {
    icon.className = 'fas fa-info-circle me-1';
  }
  alertDiv.appendChild(icon);
  
  // 添加消息文本
  const textNode = document.createTextNode(' ' + message);
  alertDiv.appendChild(textNode);
  
  // 添加关闭按钮
  const closeButton = document.createElement('button');
  closeButton.type = 'button';
  closeButton.className = 'btn-close';
  closeButton.setAttribute('data-bs-dismiss', 'alert');
  closeButton.setAttribute('aria-label', 'Close');
  alertDiv.appendChild(closeButton);
  
  // 添加到容器
  container.appendChild(alertDiv);
  
  // 设置自动消失
  setTimeout(function() {
    alertDiv.classList.add('fade-out');
    setTimeout(function() {
      if (alertDiv.parentNode) {
        alertDiv.parentNode.removeChild(alertDiv);
      }
    }, 500);
  }, 5000);
}

// 全局Toast消息显示函数
function showToast(message, type) {
    console.log("调用showToast:", message, type);
    
    if (typeof toastr === 'undefined') {
        console.error("Toastr库未加载，使用备用方法显示消息");
        alert(message);
        return;
    }
    
    // 确保类型有效
    type = type || 'info';
    
    // 映射类型到toastr方法
    switch(type.toLowerCase()) {
        case 'success':
            toastr.success(message);
            break;
        case 'error':
        case 'danger':
            toastr.error(message);
            break;
        case 'warning':
            toastr.warning(message);
            break;
        case 'info':
        default:
            toastr.info(message);
            break;
    }
    
    console.log("Toast已显示:", type, message);
}

// 测试toast是否工作的函数
function testToast() {
    console.log("测试Toast显示...");
    showToast("这是一个测试消息", "success");
} 