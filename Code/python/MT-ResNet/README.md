# Buck转换器仿真系统

这是一个基于Python和MATLAB的Buck转换器仿真系统，可以自动运行Simulink仿真并实时显示结果。

## 功能特点

- 🚀 自动启动MATLAB桌面界面
- 📊 实时显示Simulink模型
- ⚡ 自动运行仿真过程
- 📈 实时显示仿真进度
- 💾 自动保存结果到CSV文件
- 🎯 优化的显示设置和用户体验

## 系统要求

- Windows 10/11
- Python 3.7+
- MATLAB R2018b+
- Simulink工具箱

## 安装依赖

```bash
pip install matlabengine
```

## 使用方法

### 方法1: 直接运行Python脚本
```bash
cd "E:\AI-based optimized design\Code\python"
python Buck-Data.py
```

### 方法2: 使用批处理文件（推荐）
双击运行 `run_simulation.bat` 文件

## 文件结构

```
Code/python/
├── Buck-Data.py          # 主仿真脚本
├── run_simulation.bat    # Windows启动器
└── README.md            # 说明文档
```

## 运行流程

1. **启动MATLAB**: 自动启动MATLAB桌面界面
2. **加载模型**: 加载并显示Simulink模型
3. **运行仿真**: 执行BuckData.m脚本
4. **显示结果**: 在MATLAB界面中查看结果
5. **保存数据**: 自动保存到CSV文件

## 显示设置

系统会自动设置以下Simulink显示参数：
- 显示端口数据类型
- 显示线缆尺寸
- 优化模型可视化效果

## 输出文件

仿真结果将保存到：
```
Data/Input_Data/buck_data_test.csv
```

包含以下参数：
- 输出电压 (Uo)
- 开关频率 (f)
- 电感值 (L)
- 电容值 (C)
- 开关管导通电阻 (Ron)
- 电感等效电阻 (RL)
- 电容等效电阻 (RC)
- 各种功率损耗
- 效率 (Efficiency)

## 故障排除

### 常见问题

1. **MATLAB启动失败**
   - 确保MATLAB已正确安装
   - 检查许可证是否有效

2. **找不到模型文件**
   - 检查Simulink模型路径是否正确
   - 确保模型文件存在

3. **仿真运行失败**
   - 检查MATLAB脚本语法
   - 查看错误日志

### 技术支持

如果遇到问题，请检查：
- Python和MATLAB版本兼容性
- 文件路径是否正确
- 依赖包是否已安装

## 更新日志

- v2.0: 添加MATLAB界面显示和实时监控
- v1.0: 基础仿真功能

## 许可证

本项目仅供学习和研究使用。
