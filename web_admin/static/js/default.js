/**
 * 默认JavaScript文件 - 作为资源加载失败时的备选
 * 提供基本的UI功能
 */

// 确保jQuery存在或提供基本的替代功能
if (typeof jQuery === 'undefined') {
    // 简单的DOM选择器
    window.$ = function(selector) {
        if (selector.startsWith('#')) {
            return document.getElementById(selector.substring(1));
        } else if (selector.startsWith('.')) {
            return document.getElementsByClassName(selector.substring(1));
        } else {
            return document.getElementsByTagName(selector);
        }
    };
    
    // 简单的DOM就绪事件
    window.$(document).ready = function(callback) {
        if (document.readyState !== 'loading') {
            callback();
        } else {
            document.addEventListener('DOMContentLoaded', callback);
        }
    };
}

// 基本的警告框功能
function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts-container');
    if (!alertsContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type || 'info'} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alertDiv);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// 基本的表单验证
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// 注册通用事件处理器
document.addEventListener('DOMContentLoaded', function() {
    // 为所有关闭按钮添加事件处理
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) alert.remove();
        });
    });
    
    // 为表单添加验证
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(this.id)) {
                event.preventDefault();
                showAlert('请填写所有必填字段', 'warning');
            }
        });
    });
    
    console.log('默认JS脚本已加载 - 提供基本功能');
}); 