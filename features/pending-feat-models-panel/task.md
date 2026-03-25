# 任务分解：模型配置页面完善

## 概述

完善 Tauri 桌面应用的模型配置页面，连接后端 API，实现 Provider 配置管理和模型选择功能。

## 任务列表

### 任务 1：扩展后端 Provider API

**文件**: `anyclaw/api/routes/config.py`

**描述**: 扩展配置 API，支持 Provider 级别的 CRUD 操作和连接测试

**要点**:
- `GET /api/providers` - 获取所有 Provider 列表（含配置状态）
- `GET /api/providers/{name}` - 获取单个 Provider 配置
- `PUT /api/providers/{name}` - 更新 Provider 配置（含持久化）
- `POST /api/providers/{name}/test` - 测试 Provider 连接
- 修改现有 `PUT /api/config` 支持持久化到文件

**API 设计**:
```python
@router.get("/providers")
async def list_providers() -> list[ProviderInfo]:
    """获取所有 Provider 列表"""
    pass

@router.get("/providers/{name}")
async def get_provider(name: str) -> ProviderConfig:
    """获取单个 Provider 配置"""
    pass

@router.put("/providers/{name}")
async def update_provider(name: str, config: ProviderConfigUpdate) -> dict:
    """更新 Provider 配置并持久化"""
    pass

@router.post("/providers/{name}/test")
async def test_provider(name: str) -> TestResult:
    """测试 Provider 连接"""
    pass
```

**验收标准**:
- [ ] Provider 列表 API 正常工作
- [ ] Provider 配置可正确读取
- [ ] Provider 配置更新后持久化到 config.toml
- [ ] 连接测试返回正确结果

---

### 任务 2：创建 Provider 连接测试服务

**文件**: `anyclaw/api/services/provider_tester.py` (新建)

**描述**: 创建 Provider 连接测试服务，验证 API Key 和 Endpoint 是否有效

**要点**:
- 支持不同 Provider 的测试策略（OpenAI、Anthropic、ZAI 等）
- 调用轻量级 API（如 models 列表）验证连接
- 返回详细错误信息（认证失败、网络错误、超时等）
- 超时控制

**代码示例**:
```python
class ProviderTester:
    async def test_connection(self, provider: str, config: ProviderConfig) -> TestResult:
        """测试 Provider 连接"""
        if provider == "openai":
            return await self._test_openai(config)
        elif provider == "anthropic":
            return await self._test_anthropic(config)
        elif provider == "zai":
            return await self._test_zai(config)
        # ...
```

**验收标准**:
- [ ] OpenAI Provider 测试正常
- [ ] Anthropic Provider 测试正常
- [ ] ZAI/GLM Provider 测试正常
- [ ] 错误信息清晰友好

---

### 任务 3：创建前端 Provider Hooks

**文件**: `tauri-app/src/hooks/useProviders.ts` (新建)

**描述**: 创建 Provider 管理的 React Hooks

**要点**:
- `useProviders()` - 获取 Provider 列表
- `useProvider(name)` - 获取单个 Provider 配置
- `useUpdateProvider()` - 更新 Provider 配置
- `useTestProvider()` - 测试 Provider 连接

**代码示例**:
```typescript
export function useProviders(port?: number) {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${baseUrl}/api/providers`)
      .then(res => res.json())
      .then(data => {
        setProviders(data);
        setIsLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setIsLoading(false);
      });
  }, [port]);

  return { providers, isLoading, error, refetch: () => {} };
}
```

**验收标准**:
- [ ] Hooks 正确获取数据
- [ ] 错误处理完善
- [ ] 支持 refetch 刷新

---

### 任务 4：重构 ModelsPanel 组件

**文件**: `tauri-app/src/components/settings/ModelsPanel.tsx`

**描述**: 移除 mock 数据，连接后端 API，实现完整的 Provider 配置 UI

**要点**:
- 使用 `useProviders` hook 获取数据
- Provider 配置卡片（显示名称、配置状态、API Key 输入、Base URL 输入）
- 模型选择下拉框（从 Provider 获取可用模型列表）
- 连接测试按钮（显示测试状态和结果）
- 保存按钮（更新配置并持久化）

**UI 结构**:
```
ModelsPanel
├── Provider 列表
│   ├── ProviderCard (OpenAI)
│   │   ├── API Key 输入框（显示/隐藏按钮）
│   │   ├── Base URL 输入框
│   │   ├── 模型选择下拉框
│   │   ├── 测试连接按钮
│   │   └── 保存按钮
│   ├── ProviderCard (Anthropic)
│   └── ProviderCard (ZAI/GLM)
└── 添加自定义 Provider 按钮
```

**验收标准**:
- [ ] 移除所有 mock 数据
- [ ] Provider 列表从 API 获取
- [ ] API Key 输入和保存正常
- [ ] 模型选择正常
- [ ] 连接测试正常显示结果

---

### 任务 5：增强 ProviderSettings 组件

**文件**: `tauri-app/src/components/settings/ProviderSettings.tsx`

**描述**: 增强现有 ProviderSettings 组件，支持更多配置项和更好的 UX

**要点**:
- 添加"配置状态"指示器（已配置/未配置）
- 添加 Base URL 配置（用于自定义端点）
- 优化连接测试 UI（加载状态、成功/失败动画）
- 添加 i18n 支持

**验收标准**:
- [ ] 配置状态正确显示
- [ ] Base URL 配置正常
- [ ] 连接测试 UX 优化
- [ ] i18n 支持

---

### 任务 6：添加类型定义

**文件**: `tauri-app/src/types/providers.ts` (新建)

**描述**: 创建 Provider 相关的 TypeScript 类型定义

**类型定义**:
```typescript
export interface Provider {
  name: string;
  display_name: string;
  api_key?: string;
  base_url?: string;
  is_configured: boolean;
  models: string[];
  default_model?: string;
}

export interface ProviderConfig {
  api_key?: string;
  base_url?: string;
}

export interface TestResult {
  success: boolean;
  message: string;
  latency_ms?: number;
  error_code?: string;
}
```

**验收标准**:
- [ ] 类型定义完整
- [ ] 与后端 API 响应匹配

---

### 任务 7：添加 i18n 翻译

**文件**: `tauri-app/src/i18n/locales/zh.ts`, `tauri-app/src/i18n/locales/en.ts`

**描述**: 添加模型配置页面的国际化翻译

**翻译键**:
```typescript
settings: {
  // 现有...
  providerConfig: "Provider 配置",
  apiKey: "API Key",
  baseUrl: "Base URL",
  testConnection: "测试连接",
  testing: "测试中...",
  connectionSuccess: "连接成功",
  connectionFailed: "连接失败",
  configured: "已配置",
  notConfigured: "未配置",
  setDefault: "设为默认",
  customModel: "自定义模型",
  addProvider: "添加 Provider",
}
```

**验收标准**:
- [ ] 中文翻译完整
- [ ] 英文翻译完整

---

## 依赖关系

```
任务 1 (后端 API) ← 任务 2 (连接测试)
         ↓
任务 3 (前端 Hooks)
         ↓
任务 6 (类型定义)
         ↓
任务 4 (ModelsPanel) ← 任务 5 (ProviderSettings) ← 任务 7 (i18n)
```

## 预估工作量

| 任务 | 预估时间 |
|------|----------|
| 任务 1 | 1.5 小时 |
| 任务 2 | 1 小时 |
| 任务 3 | 45 分钟 |
| 任务 4 | 1.5 小时 |
| 任务 5 | 45 分钟 |
| 任务 6 | 15 分钟 |
| 任务 7 | 30 分钟 |
| **总计** | **6 小时** |
