/**
 * 超级优雅的Toast通知系统
 * 支持自动消失、进度条、不同类型的提示
 */

class ToastSystem {
  constructor() {
    this.container = null;
    this.toasts = {};
    this.counter = 0;
    this.messageSet = new Set(); // 用于跟踪已显示的消息
    this.initContainer();
  }

  initContainer() {
    // 检查容器是否已存在
    const existingContainer = document.querySelector('.toast-notification-container');
    if (existingContainer) {
      this.container = existingContainer;
      return;
    }

    // 创建新容器
    this.container = document.createElement('div');
    this.container.className = 'toast-notification-container';
    document.body.appendChild(this.container);
  }

  show(message, type = 'success', duration = 5000) {
    // 检查消息是否已经显示，避免重复
    const messageKey = `${message}-${type}`;
    if (this.messageSet.has(messageKey)) {
      return null; // 如果消息已存在，不再显示
    }
    
    // 记录这条消息已被显示
    this.messageSet.add(messageKey);
    
    // 限制消息长度，防止过长消息撑大toast宽度
    let displayMessage = message;
    if (message.length > 40) {
      displayMessage = message.substring(0, 37) + '...';
    }
    
    const id = `toast-${++this.counter}`;
    
    // 创建Toast元素
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.id = id;
    
    // 图标映射
    const iconMap = {
      success: '<i class="fas fa-check-circle"></i>',
      error: '<i class="fas fa-times-circle"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      info: '<i class="fas fa-info-circle"></i>',
      logout: '<i class="fas fa-sign-out-alt"></i>'
    };
    
    // 构建Toast内部HTML
    toast.innerHTML = `
      <div class="toast-content">
        <div class="toast-icon">${iconMap[type] || iconMap.info}</div>
        <div class="toast-message">${displayMessage}</div>
        <button class="toast-close-button" aria-label="关闭">
          <i class="fas fa-times"></i>
        </button>
        <div class="toast-progress">
          <div class="toast-progress-bar"></div>
        </div>
      </div>
    `;
    
    // 添加到容器
    this.container.appendChild(toast);
    
    // 保存引用
    this.toasts[id] = {
      element: toast,
      timeout: setTimeout(() => this.hide(id, messageKey), duration) // 传递messageKey
    };
    
    // 添加点击关闭事件
    const closeButton = toast.querySelector('.toast-close-button');
    if (closeButton) {
      closeButton.addEventListener('click', () => this.hide(id, messageKey)); // 传递messageKey
    }
    
    // 重设动画用于刷新
    void toast.offsetWidth;
    
    return id;
  }

  hide(id, messageKey = null) {
    const toast = this.toasts[id];
    if (!toast) return;
    
    clearTimeout(toast.timeout);
    
    const element = toast.element;
    element.classList.add('toast-exit');
    
    // 等待动画完成后移除
    setTimeout(() => {
      if (element.parentNode) {
        element.parentNode.removeChild(element);
      }
      delete this.toasts[id];
      
      // 消息关闭后从Set中移除，允许将来再次显示相同消息
      if (messageKey) {
        this.messageSet.delete(messageKey);
      }
    }, 300); // 匹配CSS动画时长
  }

  success(message, duration = 5000) {
    return this.show(message, 'success', duration);
  }

  error(message, duration = 5000) {
    return this.show(message, 'error', duration);
  }

  warning(message, duration = 5000) {
    return this.show(message, 'warning', duration);
  }

  info(message, duration = 5000) {
    return this.show(message, 'info', duration);
  }
  
  logout(message, duration = 5000) {
    return this.show(message, 'logout', duration);
  }
  
  // 清除所有toast
  clearAll() {
    Object.keys(this.toasts).forEach(id => this.hide(id));
    this.messageSet.clear();
  }
}

// 创建全局实例
const toast = new ToastSystem();

// 处理现有的flash消息
document.addEventListener('DOMContentLoaded', () => {
  // 清除可能存在的旧Toast
  toast.clearAll();
  
  // 阻止多次处理的标记
  let hasProcessedFlash = false;
  
  // 查找所有flash消息
  const flashMessages = document.querySelectorAll('.alert');
  
  if (flashMessages.length > 0 && !hasProcessedFlash) {
    hasProcessedFlash = true;
    
    flashMessages.forEach(flashMsg => {
      let type = 'info';
      if (flashMsg.classList.contains('alert-success')) {
        type = 'success';
      } else if (flashMsg.classList.contains('alert-danger')) {
        type = 'error';
      } else if (flashMsg.classList.contains('alert-warning')) {
        type = 'warning';
      }
      
      const message = flashMsg.textContent.trim();
      // 检查消息内容是否包含登出成功信息
      if (message.includes('退出登录成功') || message.includes('已退出登录')) {
        type = 'logout';
      }
      
      if (message) {
        // 显示为Toast
        toast.show(message, type);
        
        // 隐藏原来的消息
        flashMsg.style.display = 'none';
      }
    });
    
    return; // 已处理完消息，不再处理hidden元素中的消息
  }
  
  // 检查特殊隐藏数据字段中是否有flash消息
  const flashData = document.getElementById('flashMessageData');
  if (flashData && flashData.getAttribute('data-has-message') === 'true' && !hasProcessedFlash) {
    hasProcessedFlash = true;
    
    // 获取消息内容和类型
    const category = flashData.getAttribute('data-message-category');
    const text = flashData.getAttribute('data-message-text');
    
    if (text) {
      let type = category;
      if (category === 'danger') type = 'error';
      if (text.includes('退出登录成功') || text.includes('已退出登录')) {
        type = 'logout';
      }
      
      // 显示为Toast
      toast.show(text, type);
    }
  }
}); 