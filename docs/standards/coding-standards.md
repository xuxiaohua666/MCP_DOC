# MCP文档服务器 - 代码开发规范

## 通用规范

### 语言和编码规范
- **日志语言**: 必须使用英文
- **注释语言**: 必须使用中文
- **文件编码**: UTF-8
- **行结束符**: LF (Unix风格)

### 日志规范
- **最低日志级别**: info
- **日志格式**: 结构化日志，包含时间戳、级别、模块名称、消息
- **关键操作必须记录**: 模块初始化、重要业务操作、错误处理

### 命名规范

#### 通用命名原则
- 使用有意义的英文名称
- 避免缩写，除非是广泛认知的缩写
- 保持命名的一致性

## Java开发规范

### 代码结构
```java
package com.project.module;

import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * 中文注释：模块功能的详细说明
 * 
 * @author 开发者名称
 * @version 1.0.0
 * @since 2025-01-01
 */
public class ExampleService {
    
    private static final Logger logger = LoggerFactory.getLogger(ExampleService.class);
    
    /**
     * 中文注释：方法功能说明
     * 
     * @param param1 参数1的说明
     * @param param2 参数2的说明
     * @return 返回值说明
     * @throws Exception 异常说明
     */
    public Result processData(String param1, Integer param2) throws Exception {
        logger.info("Processing data with params: param1={}, param2={}", param1, param2);
        
        try {
            // 中文注释：核心业务逻辑
            Result result = performBusinessLogic(param1, param2);
            
            logger.info("Data processing completed successfully");
            return result;
            
        } catch (Exception e) {
            logger.error("Failed to process data: {}", e.getMessage(), e);
            throw new ProcessingException("Data processing failed", e);
        }
    }
}
```

### Java具体规范
- **类名**: 大驼峰命名法 (PascalCase)
- **方法名**: 小驼峰命名法 (camelCase)
- **常量名**: 全大写，下划线分隔 (UPPER_SNAKE_CASE)
- **包名**: 全小写，域名反写
- **日志框架**: 使用SLF4J + Logback
- **异常处理**: 必须记录错误日志，使用合适的日志级别

### Java日志示例
```java
// 中文注释：正确的日志使用方式
logger.info("User login attempt: username={}", username);
logger.warn("Invalid configuration detected: {}", configKey);
logger.error("Database connection failed: {}", e.getMessage(), e);
```

## GDScript开发规范

### 代码结构
```gdscript
extends Node
class_name ExampleService

# 中文注释：类的功能说明和用途
# 这个服务负责处理游戏中的数据操作

# 中文注释：导出变量说明
@export var max_connections: int = 10
@export var timeout_seconds: float = 5.0

# 中文注释：私有变量
var _current_connections: int = 0
var _logger: Logger

func _ready() -> void:
	# 中文注释：初始化日志系统
	_logger = Logger.new()
	_logger.info("ExampleService initialized with max_connections: %d" % max_connections)

# 中文注释：处理数据的主要方法
# @param data: 输入数据
# @param options: 处理选项
# @return: 处理结果
func process_data(data: Dictionary, options: Dictionary = {}) -> Dictionary:
	_logger.info("Processing data with %d entries" % data.size())
	
	var result: Dictionary = {}
	
	try:
		# 中文注释：执行核心业务逻辑
		result = _perform_business_logic(data, options)
		_logger.info("Data processing completed successfully")
		
	except Exception as e:
		_logger.error("Failed to process data: %s" % e.message)
		result["error"] = e.message
	
	return result
```

### GDScript具体规范
- **类名**: 大驼峰命名法 (PascalCase)
- **方法名**: 蛇形命名法 (snake_case)
- **变量名**: 蛇形命名法 (snake_case)
- **常量名**: 全大写蛇形命名法 (UPPER_SNAKE_CASE)
- **私有成员**: 以下划线开头
- **信号名**: 蛇形命名法 (snake_case)
- **日志框架**: 使用Godot内置日志或自定义Logger类

### GDScript日志示例
```gdscript
# 中文注释：正确的日志使用方式
_logger.info("Player connected: id=%s, name=%s" % [player_id, player_name])
_logger.warn("Low memory warning: available=%d MB" % available_memory)
_logger.error("Network connection failed: %s" % error_message)
```

## 文档规范

### 注释要求
1. **类注释**: 必须包含功能说明、作者、版本信息
2. **方法注释**: 必须包含功能说明、参数说明、返回值说明
3. **复杂逻辑注释**: 关键算法和业务逻辑必须添加中文注释

### README文件规范
- 使用Markdown格式
- 包含项目概述、安装说明、使用示例
- 遵循MCP文档模板结构

## 测试规范

### 测试覆盖率
- **最低要求**: 70%
- **推荐目标**: 85%
- **关键模块**: 90%以上

### 测试命名
```java
// Java测试命名示例
@Test
public void should_ReturnValidResult_When_InputIsValid() {
    // 中文注释：测试逻辑
}
```

```gdscript
# GDScript测试命名示例
func test_should_return_valid_result_when_input_is_valid():
	# 中文注释：测试逻辑
	pass
```

## 性能规范

### 代码性能
- 避免在循环中进行昂贵操作
- 合理使用缓存机制
- 及时释放资源

### 日志性能
- 使用参数化日志避免字符串拼接
- 在生产环境中合理设置日志级别
- 避免在高频调用的方法中使用debug日志

## 安全规范

### 输入验证
- 所有外部输入必须验证
- 使用白名单而不是黑名单
- 防止注入攻击

### 日志安全
- 不在日志中记录敏感信息
- 对敏感参数进行脱敏处理

```java
// 中文注释：正确的敏感信息处理
logger.info("User authentication: username={}, result={}", 
    SecurityUtils.maskSensitive(username), result);
```

## AI集成规范

### 代码可读性
- 保持方法简洁，单一职责
- 使用清晰的变量和方法名
- 避免过度复杂的嵌套

### 元数据维护
- 及时更新模块metadata.json
- 记录重要的设计决策
- 保持文档与代码的同步

## 版本控制规范

### 提交消息格式
```
type(scope): description

type: feat|fix|docs|style|refactor|test|chore
scope: 模块名称
description: 中文描述
```

### 分支策略
- `main`: 主分支，稳定版本
- `develop`: 开发分支
- `feature/`: 功能分支
- `hotfix/`: 热修复分支

---
*此文档由MCP文档服务器维护，遵循统一的AI编码指导原则*
