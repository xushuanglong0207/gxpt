#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import json
import pytest
import traceback
from datetime import datetime
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from concurrent.futures import ThreadPoolExecutor


class UiTestRunner:
    """UI测试运行器，用于执行UI自动化测试"""
    
    def __init__(self, config, parallel=1, tags=None, submodule=None):
        """
        初始化UI测试运行器
        
        Args:
            config: 配置管理器实例
            parallel: 并行执行的线程数
            tags: 要执行的测试标签
            submodule: 要执行的子模块，如 'login', 'dashboard' 等
        """
        self.config = config
        self.parallel = parallel
        self.tags = tags
        self.submodule = submodule
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.ui_config = config.get_ui_config()
        self.browser_type = self.ui_config.get('browser', 'chrome')
        self.headless = self.ui_config.get('headless', True)
        self.base_url = self.ui_config.get('base_url', '')
        self.timeout = self.ui_config.get('timeout', 30)
        self.screenshot_dir = os.path.join(self.base_dir, "screenshots")
        
        # 如果指定了子模块，加载子模块配置
        if submodule:
            module_config = config.get_module_config(f'ui.{submodule}')
            if module_config:
                # 更新基础配置
                if 'base_url' in module_config:
                    self.base_url = module_config['base_url']
                if 'browser' in module_config:
                    self.browser_type = module_config['browser']
                if 'headless' in module_config:
                    self.headless = module_config['headless']
                if 'timeout' in module_config:
                    self.timeout = module_config['timeout']
        
        # 确保截图目录存在
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
    
    def run(self):
        """
        运行UI测试
        
        Returns:
            测试结果列表
        """
        logger.info("开始执行UI测试")
        if self.submodule:
            logger.info(f"子模块: {self.submodule}")
        
        # 获取测试用例
        test_cases = self._get_test_cases()
        logger.info(f"找到 {len(test_cases)} 个UI测试用例")
        
        # 如果没有测试用例，返回空列表
        if not test_cases:
            logger.warning("没有找到符合条件的UI测试用例")
            return []
        
        # 执行测试用例
        results = []
        if self.parallel > 1 and len(test_cases) > 1:
            # 并行执行
            logger.info(f"使用 {self.parallel} 个线程并行执行UI测试")
            with ThreadPoolExecutor(max_workers=self.parallel) as executor:
                futures = [executor.submit(self._execute_test_case, test_case) for test_case in test_cases]
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)
        else:
            # 串行执行
            logger.info("串行执行UI测试")
            for test_case in test_cases:
                result = self._execute_test_case(test_case)
                if result:
                    results.append(result)
        
        logger.info(f"UI测试执行完成，共 {len(results)} 个结果")
        return results
    
    def _get_test_cases(self):
        """获取测试用例"""
        test_cases = []
        
        # 确定测试用例目录
        if self.submodule:
            test_dir = os.path.join(self.base_dir, "testcases", self.submodule)
        else:
            test_dir = os.path.join(self.base_dir, "testcases")
        
        # 如果测试用例目录不存在，返回空列表
        if not os.path.exists(test_dir):
            logger.warning(f"测试用例目录不存在: {test_dir}")
            return []
        
        # 遍历测试用例目录
        for root, _, files in os.walk(test_dir):
            for file in files:
                # 只处理JSON文件
                if file.endswith(".json"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            test_case = json.load(f)
                        
                        # 如果指定了标签，检查测试用例是否包含该标签
                        if self.tags and not self._match_tags(test_case.get("tags", [])):
                            continue
                        
                        # 添加子模块信息
                        if self.submodule:
                            test_case["submodule"] = self.submodule
                        else:
                            # 从路径中提取子模块
                            rel_path = os.path.relpath(file_path, os.path.join(self.base_dir, "testcases"))
                            parts = os.path.dirname(rel_path).split(os.sep)
                            if parts and parts[0]:
                                test_case["submodule"] = parts[0]
                        
                        test_case["file_path"] = file_path
                        test_cases.append(test_case)
                    except Exception as e:
                        logger.error(f"加载测试用例失败: {file_path}, 错误: {str(e)}")
        
        return test_cases
    
    def _match_tags(self, case_tags):
        """检查测试用例标签是否匹配"""
        if not self.tags:
            return True
        
        # 将标签字符串拆分为列表
        tag_list = self.tags.split(",") if isinstance(self.tags, str) else self.tags
        
        # 检查是否有任何一个标签匹配
        for tag in tag_list:
            if tag.strip() in case_tags:
                return True
        
        return False
    
    def _create_driver(self):
        """创建WebDriver实例"""
        if self.browser_type.lower() == "chrome":
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        elif self.browser_type.lower() == "firefox":
            options = FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        
        elif self.browser_type.lower() == "edge":
            options = EdgeOptions()
            if self.headless:
                options.add_argument("--headless")
            
            driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
        
        else:
            logger.warning(f"不支持的浏览器类型: {self.browser_type}，将使用Chrome")
            options = ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 设置隐式等待时间
        driver.implicitly_wait(self.timeout)
        
        return driver
    
    def _execute_test_case(self, test_case):
        """
        执行单个测试用例
        
        Args:
            test_case: 测试用例数据
            
        Returns:
            测试结果字典
        """
        name = test_case.get("name", "未命名测试")
        description = test_case.get("description", "")
        url = test_case.get("url", self.base_url)
        steps = test_case.get("steps", [])
        submodule = test_case.get("submodule", "")
        
        # 初始化结果
        result = {
            "name": name,
            "description": description,
            "module": "ui",
            "submodule": submodule,
            "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "start_timestamp": int(time.time() * 1000),
            "status": "skipped",
            "duration": 0,
            "error": "",
            "traceback": "",
            "screenshots": []
        }
        
        driver = None
        try:
            logger.info(f"执行UI测试: {name}")
            
            # 创建WebDriver实例
            driver = self._create_driver()
            
            # 记录开始时间
            start_time = time.time()
            
            # 打开URL
            if url:
                logger.debug(f"打开URL: {url}")
                driver.get(url)
            
            # 执行测试步骤
            for i, step in enumerate(steps):
                step_name = step.get("name", f"步骤 {i+1}")
                step_action = step.get("action", "")
                step_locator = step.get("locator", {})
                step_value = step.get("value", "")
                step_wait = step.get("wait", 0)
                
                logger.debug(f"执行步骤: {step_name}")
                
                # 执行动作
                self._execute_step(driver, step_action, step_locator, step_value)
                
                # 等待
                if step_wait > 0:
                    time.sleep(step_wait)
                
                # 截图
                if step.get("screenshot", False):
                    screenshot_path = self._take_screenshot(driver, f"{name}_{i+1}_{step_name}")
                    result["screenshots"].append(screenshot_path)
            
            # 计算耗时
            duration = time.time() - start_time
            result["duration"] = duration
            
            # 测试通过
            result["status"] = "passed"
            logger.info(f"测试通过: {name}, 耗时: {duration:.2f}秒")
            
            # 最终截图
            screenshot_path = self._take_screenshot(driver, f"{name}_final")
            result["screenshots"].append(screenshot_path)
        
        except Exception as e:
            # 测试执行异常
            result["status"] = "failed"
            result["error"] = f"测试执行异常: {str(e)}"
            result["traceback"] = traceback.format_exc()
            logger.error(f"测试执行异常: {name}, 错误: {str(e)}")
            
            # 错误截图
            if driver:
                screenshot_path = self._take_screenshot(driver, f"{name}_error")
                result["screenshots"].append(screenshot_path)
        
        finally:
            # 关闭浏览器
            if driver:
                driver.quit()
            
            # 记录结束时间
            result["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["end_timestamp"] = int(time.time() * 1000)
        
        return result
    
    def _execute_step(self, driver, action, locator, value):
        """
        执行测试步骤
        
        Args:
            driver: WebDriver实例
            action: 动作名称
            locator: 定位器
            value: 值
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys
        
        # 获取定位方式和表达式
        locator_type = locator.get("type", "css")
        locator_value = locator.get("value", "")
        
        # 映射定位方式
        locator_map = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH
        }
        
        by = locator_map.get(locator_type.lower(), By.CSS_SELECTOR)
        
        # 等待元素可见
        if locator_value:
            element = WebDriverWait(driver, self.timeout).until(
                EC.visibility_of_element_located((by, locator_value))
            )
        
        # 执行动作
        if action.lower() == "click":
            element.click()
        
        elif action.lower() == "input":
            element.clear()
            element.send_keys(value)
        
        elif action.lower() == "select":
            from selenium.webdriver.support.ui import Select
            select = Select(element)
            select.select_by_visible_text(value)
        
        elif action.lower() == "hover":
            ActionChains(driver).move_to_element(element).perform()
        
        elif action.lower() == "submit":
            element.submit()
        
        elif action.lower() == "clear":
            element.clear()
        
        elif action.lower() == "press_key":
            # 映射特殊键
            key_map = {
                "enter": Keys.ENTER,
                "tab": Keys.TAB,
                "escape": Keys.ESCAPE,
                "space": Keys.SPACE,
                "backspace": Keys.BACKSPACE,
                "delete": Keys.DELETE,
                "arrow_up": Keys.ARROW_UP,
                "arrow_down": Keys.ARROW_DOWN,
                "arrow_left": Keys.ARROW_LEFT,
                "arrow_right": Keys.ARROW_RIGHT
            }
            
            key = key_map.get(value.lower(), value)
            element.send_keys(key)
        
        elif action.lower() == "wait":
            time.sleep(float(value) if value else 1)
        
        elif action.lower() == "assert_text":
            assert value in element.text, f"断言失败: 期望文本 '{value}' 不在实际文本 '{element.text}' 中"
        
        elif action.lower() == "assert_value":
            assert value == element.get_attribute("value"), f"断言失败: 期望值 '{value}' 不等于实际值 '{element.get_attribute('value')}'"
        
        elif action.lower() == "assert_visible":
            assert element.is_displayed(), "断言失败: 元素不可见"
        
        elif action.lower() == "assert_not_visible":
            assert not element.is_displayed(), "断言失败: 元素可见"
        
        elif action.lower() == "assert_enabled":
            assert element.is_enabled(), "断言失败: 元素不可用"
        
        elif action.lower() == "assert_disabled":
            assert not element.is_enabled(), "断言失败: 元素可用"
        
        elif action.lower() == "assert_selected":
            assert element.is_selected(), "断言失败: 元素未被选中"
        
        elif action.lower() == "assert_not_selected":
            assert not element.is_selected(), "断言失败: 元素被选中"
        
        elif action.lower() == "execute_script":
            driver.execute_script(value)
        
        elif action.lower() == "scroll_to":
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
        
        elif action.lower() == "refresh":
            driver.refresh()
        
        elif action.lower() == "back":
            driver.back()
        
        elif action.lower() == "forward":
            driver.forward()
        
        else:
            raise ValueError(f"不支持的动作: {action}")
    
    def _take_screenshot(self, driver, name):
        """
        截图
        
        Args:
            driver: WebDriver实例
            name: 截图名称
            
        Returns:
            截图路径
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png".replace(" ", "_")
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            driver.save_screenshot(filepath)
            logger.debug(f"截图已保存: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return None 