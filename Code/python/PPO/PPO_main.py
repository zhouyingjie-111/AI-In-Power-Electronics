"""
Buck变换器PPO优化系统运行脚本
=====================================

本脚本是PPO训练系统的主入口，负责：
1. 检查必要的依赖包和文件
2. 解析命令行参数
3. 协调训练和可视化流程
4. 提供友好的用户界面和错误提示

使用方式:
    python PPO_main.py                    # 完整流程（训练+可视化）
    python PPO_main.py --train-only       # 仅训练
    python PPO_main.py --visualize-only   # 仅可视化
"""

import argparse  # 命令行参数解析
import sys       # 系统相关功能
import os        # 操作系统接口

# ==================== 环境配置 ====================
# 抑制 TensorFlow INFO 级别日志，减少控制台输出噪声
# '3' = 只显示ERROR级别的日志
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')


def main():
    """
    主程序入口函数
    
    功能流程:
        1. 解析命令行参数，确定运行模式
        2. 检查Python依赖包是否已安装
        3. 验证必要的模型和数据文件是否存在
        4. 根据参数执行训练或可视化任务
        5. 输出执行结果和文件路径
    
    Returns:
        int: 退出码，0表示成功，1表示失败
    """
    # ==================== 命令行参数解析 ====================
    # 创建参数解析器，配置帮助信息格式
    parser = argparse.ArgumentParser(
        description='Buck变换器PPO优化系统',  # 程序简短描述
        formatter_class=argparse.RawDescriptionHelpFormatter,  # 保持epilog格式
        epilog="""
示例:
    python PPO_main.py                      # 运行训练+可视化（完整流程）
    python PPO_main.py --train-only         # 仅运行PPO训练
    python PPO_main.py --visualize-only     # 仅生成可视化分析
        """
    )
    
    # 添加命令行参数选项
    # --train-only: 只训练，跳过可视化步骤
    parser.add_argument('--train-only', action='store_true',
                       help='仅运行训练，不生成可视化')
    
    # --visualize-only: 只可视化，跳过训练步骤（需要已有训练数据）
    parser.add_argument('--visualize-only', action='store_true',
                       help='仅生成可视化，不运行训练')
    
    # 解析用户输入的参数
    args = parser.parse_args()
    
    # ==================== 显示欢迎信息 ====================
    print("🚀 Buck变换器PPO优化系统")
    print("="*50)
    
    # ==================== 检查Python依赖包 ====================
    # 尝试导入所有必需的Python包，如果失败则提示用户安装
    try:
        import numpy as np                    # 数值计算
        import pandas as pd                   # 数据处理
        import matplotlib.pyplot as plt       # 绘图
        from stable_baselines3 import PPO     # PPO强化学习算法
        from keras.models import load_model   # Keras模型加载
        print("✓ 依赖检查通过")
    except ImportError as e:
        # 捕获导入错误，提示用户安装缺失的包
        print(f"❌ 缺少依赖: {e}")
        print("请安装所需依赖: pip install numpy pandas matplotlib stable-baselines3 keras")
        return 1  # 返回错误码
    
    # ==================== 检查必要文件 ====================
    # 列出训练所需的关键文件：预训练模型和标准化参数
    required_files = [
        'E:/AI-based optimized design/Trained_model/trainedNet.keras',      # MT-ResNet预训练模型
        'E:/AI-based optimized design/Data/Input_Data/x_scaled_data.csv',   # 输入标准化参数
        'E:/AI-based optimized design/Data/Input_Data/y_scaled_data.csv'    # 输出标准化参数
    ]
    
    # 检查每个文件是否存在，记录缺失的文件
    missing_files = [f for f in required_files if not os.path.exists(f)]
    if missing_files:
        # 如果有文件缺失，显示错误信息并退出
        print("❌ 缺少必要文件:")
        for f in missing_files:
            print(f"  - {f}")
        print("\n提示: 请先运行MT-ResNet训练生成必要文件")
        return 1  # 返回错误码
    
    print("✓ 必要文件检查通过")
    
    # ==================== 执行PPO训练 ====================
    # 如果用户没有指定 --visualize-only，则执行训练
    if not args.visualize_only:
        print("\n🔄 开始PPO训练...")
        try:
            # 动态导入PPO模块的main函数
            from PPO import main as train_main
            train_main()  # 执行训练
            print("✅ 训练完成")
        except Exception as e:
            # 捕获训练过程中的任何异常
            print(f"❌ 训练失败: {e}")
            import traceback
            traceback.print_exc()  # 打印详细错误堆栈
            return 1  # 返回错误码
    
    # ==================== 生成可视化分析 ====================
    # 如果用户没有指定 --train-only，则生成可视化
    if not args.train_only:
        print("\n📊 生成可视化分析...")
        try:
            # 动态导入可视化模块的main函数
            from visualize_training_results import main as viz_main
            viz_main()  # 执行可视化
            print("✅ 可视化完成")
        except Exception as e:
            # 捕获可视化过程中的任何异常
            print(f"❌ 可视化失败: {e}")
            import traceback
            traceback.print_exc()  # 打印详细错误堆栈
            return 1  # 返回错误码
    
    # ==================== 显示完成信息 ====================
    # 所有任务成功完成，显示结果文件位置
    print("\n🎉 所有任务完成！")
    print("📁 检查以下目录获取结果:")
    print("  - 模型文件:     E:/AI-based optimized design/Trained_model/")
    print("  - 可视化图表:   E:/AI-based optimized design/Visualization/")
    print("  - TensorBoard:  E:/AI-based optimized design/TensorBoard/")
    print("\n💡 提示:")
    print("  - 查看TensorBoard: tensorboard --logdir=E:/AI-based optimized design/TensorBoard")
    print("  - 优化参数保存在: Visualization/optimal_design.csv")
    
    return 0  # 返回成功码


# ==================== 程序入口点 ====================
if __name__ == '__main__':
    # 当直接运行此脚本时执行main函数
    # sys.exit()确保程序以正确的退出码结束
    sys.exit(main())
