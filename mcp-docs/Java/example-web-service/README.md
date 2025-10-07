# Example Web Service

## 项目概述
这是一个基于Spring Boot的RESTful Web服务示例项目，展示了如何在MCP文档服务器规范下构建和维护企业级Java应用。

## 技术栈
- **编程语言**: Java 17
- **主要框架**: Spring Boot 3.1.0
- **数据库**: MySQL 8.0 / H2 (测试)
- **其他依赖**: 
  - Spring Data JPA
  - Spring Web
  - SLF4J + Logback
  - JUnit 5

## 架构设计

### 整体架构
采用经典的三层架构模式：
- **控制器层 (Controller)**: 处理HTTP请求和响应
- **服务层 (Service)**: 核心业务逻辑
- **数据访问层 (Repository)**: 数据持久化

### 核心模块
- [用户管理模块](./user-management/README.md) - 用户注册、登录、信息管理
- [认证授权模块](./authentication/README.md) - JWT token管理和权限控制
- [数据访问模块](./data-access/README.md) - 数据库操作和缓存

## 功能模块

### 已实现功能
- [x] 用户注册和登录
- [x] JWT token认证
- [x] 用户信息CRUD操作
- [x] API文档自动生成
- [x] 日志记录和监控

### 计划功能
- [ ] 角色权限管理
- [ ] 文件上传下载
- [ ] 消息推送功能
- [ ] 数据统计报表

## 开发规范

### 代码规范
- 日志使用英文，注释使用中文
- 日志级别最低使用info级别
- 遵循Spring Boot最佳实践
- 使用SLF4J进行日志记录

### 文件结构
```
example-web-service/
├── README.md
├── project-info.json
├── user-management/
│   ├── README.md
│   ├── api.md
│   ├── implementation.md
│   └── metadata.json
├── authentication/
│   ├── README.md
│   ├── api.md
│   ├── implementation.md
│   └── metadata.json
└── data-access/
    ├── README.md
    ├── api.md
    ├── implementation.md
    └── metadata.json
```

## API接口

### 核心接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册
- `GET /api/users/{id}` - 获取用户信息
- `PUT /api/users/{id}` - 更新用户信息

详细API文档请参考各模块的api.md文件。

## 环境配置

### 开发环境
- JDK 17+
- Maven 3.8+
- MySQL 8.0+
- IDE: IntelliJ IDEA 推荐

### 生产环境
- Java 17 Runtime
- MySQL 8.0
- 最小内存: 512MB
- 推荐内存: 2GB

## 部署说明
1. 克隆项目代码
2. 配置数据库连接信息
3. 执行 `mvn clean package`
4. 运行 `java -jar target/example-web-service.jar`

## 测试
- **单元测试**: JUnit 5 + Mockito
- **集成测试**: Spring Boot Test
- **测试覆盖率**: 目标85%

## 版本历史
- **v1.0.0**: 基础功能实现，用户管理和认证
- **v0.9.0**: 项目初始化，架构搭建

## 贡献指南
1. 遵循代码规范
2. 提交前运行测试
3. 更新相关文档
4. 使用规范的提交消息格式

## 许可证
MIT License

---
*此文档由MCP文档服务器自动维护，最后更新时间: 2025-01-01*
