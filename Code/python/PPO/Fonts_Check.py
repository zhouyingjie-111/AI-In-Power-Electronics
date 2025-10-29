#!/usr/bin/env python3
"""
字体检测工具
============

本工具用于检测系统可用的中文字体,帮助解决matplotlib中文显示问题。

使用方法:
    python check_fonts.py

作者: AI优化设计团队
版本: 2.0
"""

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

def check_available_fonts():
    """检测系统可用字体"""
    print("🔍 检测系统可用字体...")
    print("="*60)
    
    # 获取所有字体
    all_fonts = [f.name for f in fm.fontManager.ttflist]
    unique_fonts = sorted(set(all_fonts))
    
    print(f"系统总字体数量: {len(unique_fonts)}")
    print()
    
    # 中文字体候选列表
    chinese_font_candidates = [
        'SimHei',           # Windows 黑体
        'Microsoft YaHei',  # Windows 微软雅黑
        'WenQuanYi Micro Hei',  # Linux 文泉驿微米黑
        'PingFang SC',      # macOS 苹方
        'Hiragino Sans GB', # macOS 冬青黑体
        'Arial Unicode MS', # 通用
        'STHeiti',          # 华文黑体
        'STSong',           # 华文宋体
        'STKaiti',          # 华文楷体
        'STFangsong',       # 华文仿宋
        'SimSun',           # 宋体
        'KaiTi',            # 楷体
        'FangSong',         # 仿宋
        'LiSu',             # 隶书
        'YouYuan',          # 幼圆
    ]
    
    print("🎯 中文字体检测结果:")
    print("-" * 40)
    available_chinese_fonts = []
    
    for font in chinese_font_candidates:
        if font in unique_fonts:
            available_chinese_fonts.append(font)
            print(f"✓ {font}")
        else:
            print(f"✗ {font}")
    
    print()
    print(f"可用中文字体数量: {len(available_chinese_fonts)}")
    
    if available_chinese_fonts:
        print(f"推荐使用: {available_chinese_fonts[0]}")
    else:
        print("⚠️ 未找到中文字体，建议安装中文字体包")
    
    print()
    print("📋 所有字体列表 (前50个):")
    print("-" * 40)
    for i, font in enumerate(unique_fonts[:50]):
        print(f"{i+1:2d}. {font}")
    
    if len(unique_fonts) > 50:
        print(f"... 还有 {len(unique_fonts) - 50} 个字体")
    
    return available_chinese_fonts

def test_chinese_display():
    """测试中文显示效果"""
    print("\n🧪 测试中文显示效果...")
    print("="*60)
    
    try:
        # 创建测试图形
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 测试数据
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # 绘制图形
        ax.plot(x, y1, label='正弦波', linewidth=2)
        ax.plot(x, y2, label='余弦波', linewidth=2)
        
        # 设置中文标签
        ax.set_title('中文字体显示测试', fontsize=16, fontweight='bold')
        ax.set_xlabel('时间 (秒)', fontsize=12)
        ax.set_ylabel('幅值', fontsize=12)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # 添加文本注释
        ax.text(5, 0.5, '这是中文文本测试', fontsize=14, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
        
        plt.tight_layout()
        
        # 保存测试图片
        test_path = 'E:/AI-based optimized design/Visualization/font_test.png'
        plt.savefig(test_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 测试图片已保存: {test_path}")
        print("请检查图片中的中文是否正常显示")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def setup_optimal_font():
    """设置最优字体配置"""
    print("\n⚙️ 设置最优字体配置...")
    print("="*60)
    
    available_fonts = check_available_fonts()
    
    if available_fonts:
        # 使用第一个可用的中文字体
        optimal_font = available_fonts[0]
        matplotlib.rcParams['font.sans-serif'] = [optimal_font] + available_fonts
        matplotlib.rcParams['axes.unicode_minus'] = False
        
        print(f"✓ 已设置最优字体: {optimal_font}")
        
        # 生成配置代码
        config_code = f"""
# 字体配置代码
import matplotlib
matplotlib.rcParams['font.sans-serif'] = {[optimal_font] + available_fonts}
matplotlib.rcParams['axes.unicode_minus'] = False
"""
        
        print("\n📝 建议的字体配置代码:")
        print("-" * 40)
        print(config_code)
        
    else:
        print("⚠️ 未找到中文字体，使用默认配置")
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False

def main():
    """主程序入口"""
    print("🔤 字体检测和配置工具")
    print("="*60)
    
    try:
        # 检测可用字体
        available_fonts = check_available_fonts()
        
        # 设置最优字体
        setup_optimal_font()
        
        # 测试中文显示
        test_chinese_display()
        
        print("\n✅ 字体检测完成！")
        print("\n💡 使用建议:")
        print("1. 如果中文显示正常，说明字体配置正确")
        print("2. 如果中文显示为方块，请安装中文字体")
        print("3. 在Windows上推荐安装'微软雅黑'或'黑体'")
        print("4. 在Linux上推荐安装'文泉驿微米黑'")
        print("5. 在macOS上推荐使用'苹方'或'冬青黑体'")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
