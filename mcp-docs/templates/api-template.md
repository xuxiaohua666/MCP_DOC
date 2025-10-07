# {模块名称} API文档

## API概述
<!-- API的整体描述和设计理念 -->

## 接口列表

### {接口分类1}

#### {方法名称1}
- **功能描述**: {功能说明}
- **访问路径**: `{path}`
- **请求方法**: `{HTTP_METHOD}`
- **权限要求**: {权限说明}

**请求参数**:
```json
{
  "param1": "string - {参数说明}",
  "param2": "integer - {参数说明}",
  "param3": "boolean - {参数说明}"
}
```

**响应格式**:
```json
{
  "code": "integer - 响应码",
  "message": "string - 响应消息",
  "data": {
    "result1": "string - {结果说明}",
    "result2": "integer - {结果说明}"
  }
}
```

**代码示例**:
```{language}
// 中文注释：API调用示例
{code_example}
```

**响应码说明**:
- `200`: 成功
- `400`: 参数错误
- `401`: 未授权
- `500`: 服务器内部错误

#### {方法名称2}
<!-- 类似的API文档格式 -->

### {接口分类2}
<!-- 其他接口分类 -->

## 数据模型

### {模型名称1}
```{language}
{model_definition}
```

**字段说明**:
- `field1`: {类型} - {字段说明}
- `field2`: {类型} - {字段说明}

### {模型名称2}
<!-- 其他数据模型 -->

## 错误处理

### 通用错误码
- `E001`: {错误描述}
- `E002`: {错误描述}

### 日志记录
```{language}
// 中文注释：记录API调用日志
logger.info("API called: {} with params: {}", apiName, params);

// 中文注释：记录错误信息
logger.error("API error occurred: {}", errorMessage);
```

## 性能指标
- **响应时间**: < {time}ms
- **并发支持**: {concurrent_users} 用户
- **限流策略**: {rate_limit}

## 版本兼容性
- **当前版本**: v{current_version}
- **支持版本**: v{min_version} - v{max_version}
- **废弃接口**: {deprecated_apis}

## 测试用例

### 单元测试
```{language}
// 中文注释：API单元测试示例
{test_example}
```

### 集成测试
<!-- 集成测试说明 -->

## 使用建议
<!-- API使用的最佳实践和建议 -->

---
*此文档由MCP文档服务器自动维护，最后更新时间: {timestamp}*
