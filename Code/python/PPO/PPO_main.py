"""
Buck变换器PPO优化系统运行脚本
=====================================

本脚本提供简化的接口来运行PPO优化和结果分析。
"""

import argparse
import sys
import os

# 抑制 TensorFlow INFO 级别日志
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')

"""主程序入口"""
def main():
    
    parser = argparse.ArgumentParser(
        description='Buck变换器PPO优化系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python run_optimization.py                 # 运行训练+可视化（无仿真）
    python run_optimization.py --train-only    # 仅训练
    python run_optimization.py --visualize-only # 仅可视化
        """
    )
    
    parser.add_argument('--train-only', action='store_true',
                       help='仅运行训练，不生成可视化和仿真')
    parser.add_argument('--visualize-only', action='store_true',
                       help='仅生成可视化，不运行训练和仿真')
    
    args = parser.parse_args()
    
    print("🚀 Buck变换器PPO优化系统")
    print("="*50)
    
    # 检查依赖
    try:
        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        from stable_baselines3 import PPO
        from keras.models import load_model
        print("✓ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装所需依赖: pip install numpy pandas matplotlib stable-baselines3 keras")
        return 1
    
    # 检查必要文件
    required_files = [
        'E:/AI-based optimized design/Trained_model/trainedNet.keras',
        'E:/AI-based optimized design/Data/Input_Data/x_scaled_data.csv',
        'E:/AI-based optimized design/Data/Input_Data/y_scaled_data.csv'
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        print("❌ 缺少必要文件:")
        for f in missing_files:
            print(f"  - {f}")
        return 1
    
    print("✓ 必要文件检查通过")
    
    # 运行训练（不包含仿真）
    if not args.visualize_only:
        print("\n🔄 开始PPO训练...")
        try:
            from PPO import main as train_main
            train_main()
            print("✅ 训练完成")
        except Exception as e:
            print(f"❌ 训练失败: {e}")
            return 1
    
    # 生成可视化
    if not args.train_only:
        print("\n📊 生成可视化分析...")
        try:
            from visualize_training_results import main as viz_main
            viz_main()
            print("✅ 可视化完成")
        except Exception as e:
            print(f"❌ 可视化失败: {e}")
            return 1
    
    print("\n🎉 所有任务完成！")
    print("📁 检查以下目录获取结果:")
    print("  - 模型文件: E:/AI-based optimized design/Trained_model/")
    print("  - 可视化: E:/AI-based optimized design/Visualization/")
    print("  - TensorBoard: E:/AI-based optimized design/TensorBoard/")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
