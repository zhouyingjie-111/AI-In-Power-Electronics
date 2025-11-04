"""
Buck变换器PPO训练结果可视化分析
=====================================

本脚本用于分析和可视化PPO训练结果,包括:
1. 训练进度分析
2. 参数演化过程
3. 性能指标分布
4. 最优设计参数分析
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import shutil
import sys
import subprocess
from typing import Dict, Optional, Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配置参数
class VisualizationConfig:
    # 文件路径
    HISTORY_PATH = 'E:/AI-based optimized design/Data/Training_History/training_history.npz'
    SAVE_DIR = 'E:/AI-based optimized design/Visualization/'
    
    # 参数配置（频率固定为500kHz）
    FIXED_FREQUENCY = 500e3         # 固定开关频率 (Hz)
    PARAM_BOUNDS = {
        'L(H)': (1e-6, 3e-6),       # 电感
        'C(F)': (8e-6, 10e-6),      # 电容
        'Ron': (0.002, 0.005),       # 开关管电阻
        'RL': (0.0015, 0.1),        # 电感电阻
        'RC': (0.01, 0.2)           # 电容电阻
    }
    
    PARAM_NAMES = list(PARAM_BOUNDS.keys())
    RIPPLE_THRESHOLD = 0.005        # 纹波系数上限（0.5%）
    TARGET_EFFICIENCY = 0.95
    
"""加载训练历史数据"""
def load_training_data() -> Optional[Dict]:
    try:
        if not os.path.exists(VisualizationConfig.HISTORY_PATH):
            print(f"❌ 训练历史文件不存在: {VisualizationConfig.HISTORY_PATH}")
            return None
            
        data = np.load(VisualizationConfig.HISTORY_PATH)
        print(f"✓ 成功加载训练数据")
        
        return {
            'param_history': data['param_history'],
            'ripple_history': data['ripple_history'],
            'efficiency_history': data['efficiency_history'],
            'reward_history': data['reward_history'],
            'diversity_history': data['diversity_history'],
            'boundary_distance_history': data['boundary_distance_history']
        }
    except Exception as e:
        print(f"❌ 加载训练数据失败: {e}")
        return None

"""绘制训练总览图"""
def plot_training_overview(data: Dict) -> None:
   
    print("📊 生成训练总览图...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Buck变换器PPO训练总览', fontsize=16, fontweight='bold')
    
    # 1. 奖励曲线
    axes[0, 0].plot(data['reward_history'], alpha=0.7, linewidth=1)
    axes[0, 0].set_title('训练奖励变化')
    axes[0, 0].set_xlabel('训练步数')
    axes[0, 0].set_ylabel('奖励值')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 效率变化
    axes[0, 1].plot(data['efficiency_history'], alpha=0.7, linewidth=1, color='green')
    axes[0, 1].axhline(y=VisualizationConfig.TARGET_EFFICIENCY, color='red', 
                      linestyle='--', alpha=0.7, label='目标效率 95%')
    axes[0, 1].set_title('效率变化')
    axes[0, 1].set_xlabel('训练步数')
    axes[0, 1].set_ylabel('效率')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 纹波变化
    axes[0, 2].plot(data['ripple_history'], alpha=0.7, linewidth=1, color='orange')
    axes[0, 2].axhline(y=VisualizationConfig.RIPPLE_THRESHOLD, color='red', 
                      linestyle='--', alpha=0.7, label=f'纹波阈值 {VisualizationConfig.RIPPLE_THRESHOLD*100:.1f}%')
    axes[0, 2].set_title('纹波系数变化')
    axes[0, 2].set_xlabel('训练步数')
    axes[0, 2].set_ylabel('纹波系数')
    axes[0, 2].legend()
    axes[0, 2].grid(True, alpha=0.3)
    
    # 4. 效率vs纹波散点图
    scatter = axes[1, 0].scatter(data['efficiency_history'], data['ripple_history'], 
                                c=data['reward_history'], cmap='viridis', alpha=0.6)
    axes[1, 0].axhline(y=VisualizationConfig.RIPPLE_THRESHOLD, color='red', 
                      linestyle='--', alpha=0.7, label='纹波阈值')
    axes[1, 0].axvline(x=VisualizationConfig.TARGET_EFFICIENCY, color='green', 
                      linestyle='--', alpha=0.7, label='目标效率')
    axes[1, 0].set_title('效率 vs 纹波')
    axes[1, 0].set_xlabel('效率')
    axes[1, 0].set_ylabel('纹波系数')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    plt.colorbar(scatter, ax=axes[1, 0], label='奖励值')
    
    # 5. 奖励分布
    axes[1, 1].hist(data['reward_history'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    axes[1, 1].set_title('奖励分布')
    axes[1, 1].set_xlabel('奖励值')
    axes[1, 1].set_ylabel('频次')
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. 训练稳定性（滑动平均）
    window_size = min(100, len(data['reward_history']) // 10)
    if window_size > 1:
        reward_ma = np.convolve(data['reward_history'], np.ones(window_size)/window_size, mode='valid')
        axes[1, 2].plot(reward_ma, alpha=0.8, linewidth=2, color='purple')
        axes[1, 2].set_title(f'奖励滑动平均 (窗口={window_size})')
        axes[1, 2].set_xlabel('训练步数')
        axes[1, 2].set_ylabel('平均奖励')
        axes[1, 2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    os.makedirs(VisualizationConfig.SAVE_DIR, exist_ok=True)
    save_path = os.path.join(VisualizationConfig.SAVE_DIR, 'training_overview.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 训练总览图已保存: {save_path}")

"""绘制性能分析图"""
def plot_performance_analysis(data: Dict) -> None:
    print("📊 生成性能分析图...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Buck变换器性能分析', fontsize=16, fontweight='bold')
    
    # 1. 效率分布
    axes[0, 0].hist(data['efficiency_history'], bins=50, alpha=0.7, color='green', edgecolor='black')
    axes[0, 0].axvline(x=VisualizationConfig.TARGET_EFFICIENCY, color='red', 
                      linestyle='--', alpha=0.7, label='目标效率 95%')
    axes[0, 0].set_title('效率分布')
    axes[0, 0].set_xlabel('效率')
    axes[0, 0].set_ylabel('频次')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 纹波分布
    axes[0, 1].hist(data['ripple_history'], bins=50, alpha=0.7, color='orange', edgecolor='black')
    axes[0, 1].axvline(x=VisualizationConfig.RIPPLE_THRESHOLD, color='red', 
                      linestyle='--', alpha=0.7, label=f'纹波阈值 {VisualizationConfig.RIPPLE_THRESHOLD*100:.1f}%')
    axes[0, 1].set_title('纹波系数分布')
    axes[0, 1].set_xlabel('纹波系数')
    axes[0, 1].set_ylabel('频次')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 效率vs纹波热力图
    efficiency_bins = np.linspace(0.7, 1.0, 20)
    ripple_bins = np.linspace(0, 0.1, 20)
    hist, xedges, yedges = np.histogram2d(data['efficiency_history'], data['ripple_history'], 
                                         bins=[efficiency_bins, ripple_bins])
    
    im = axes[1, 0].imshow(hist.T, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], 
                          cmap='YlOrRd', aspect='auto')
    axes[1, 0].axhline(y=VisualizationConfig.RIPPLE_THRESHOLD, color='blue', 
                      linestyle='--', alpha=0.7, label='纹波阈值')
    axes[1, 0].axvline(x=VisualizationConfig.TARGET_EFFICIENCY, color='blue', 
                      linestyle='--', alpha=0.7, label='目标效率')
    axes[1, 0].set_title('效率-纹波热力图')
    axes[1, 0].set_xlabel('效率')
    axes[1, 0].set_ylabel('纹波系数')
    axes[1, 0].legend()
    plt.colorbar(im, ax=axes[1, 0], label='频次')
    
    # 4. 训练收敛性
    window_size = min(200, len(data['reward_history']) // 20)
    if window_size > 1:
        reward_ma = np.convolve(data['reward_history'], np.ones(window_size)/window_size, mode='valid')
        axes[1, 1].plot(reward_ma, alpha=0.8, linewidth=2, color='purple', label='奖励滑动平均')
        axes[1, 1].set_title(f'训练收敛性 (窗口={window_size})')
        axes[1, 1].set_xlabel('训练步数')
        axes[1, 1].set_ylabel('平均奖励')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图片
    save_path = os.path.join(VisualizationConfig.SAVE_DIR, 'performance_analysis.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 性能分析图已保存: {save_path}")

"""分析最优设计参数"""
def analyze_optimal_designs(data: Dict) -> None: 
    print("📊 分析最优设计参数...")
    
    best = find_best_design(data)
    if best is None:
        print("⚠️ 没有找到满足约束的设计")
        return
    best_params, best_efficiency, best_ripple, best_reward = best
    
    print(f"\n🏆 最优设计参数 (奖励: {best_reward:.2f}):")
    print("="*50)
    # 显示固定频率
    print(f"{'f(Hz)':>8}: {VisualizationConfig.FIXED_FREQUENCY:>12.6g}")
    # 显示可变参数（best_params[0]是频率，从索引1开始是可变参数）
    for name, value in zip(VisualizationConfig.PARAM_NAMES, best_params[1:]):
        print(f"{name:>8}: {value:>12.6g}")
    print(f"{'效率':>8}: {best_efficiency:>12.4f} ({best_efficiency*100:.2f}%)")
    print(f"{'纹波':>8}: {best_ripple:>12.4f} ({best_ripple*100:.2f}%)")
    print("="*50)
    
    # 保存最优设计到CSV（包含固定频率和可变参数）
    optimal_design = {
        'parameter': ['f(Hz)'] + VisualizationConfig.PARAM_NAMES + ['efficiency', 'ripple', 'reward'],
        'value': [VisualizationConfig.FIXED_FREQUENCY] + list(best_params[1:]) + [best_efficiency, best_ripple, best_reward]
    }
    
    df = pd.DataFrame(optimal_design)
    save_path = os.path.join(VisualizationConfig.SAVE_DIR, 'optimal_design.csv')
    df.to_csv(save_path, index=False, encoding='utf-8')
    print(f"✓ 最优设计参数已保存: {save_path}")

def find_best_design(data: Dict) -> Optional[Tuple[np.ndarray, float, float, float]]:
    """返回(最优参数数组, 效率, 纹波, 奖励)；若无满足约束的设计则返回None"""
    eff = np.array(data['efficiency_history'])
    rip = np.array(data['ripple_history'])
    rew = np.array(data['reward_history'])
    params = np.array(data['param_history'])
    valid_mask = (rip <= VisualizationConfig.RIPPLE_THRESHOLD) & (eff >= 0.9)
    if not np.any(valid_mask):
        return None
    idx = np.argmax(rew[valid_mask])
    best_params = params[valid_mask][idx]
    return best_params, eff[valid_mask][idx], rip[valid_mask][idx], rew[valid_mask][idx]


def generate_summary_report(data: Dict) -> str:
    print("📊 生成训练摘要报告...")
    
    # 计算统计信息
    total_steps = len(data['reward_history'])
    final_reward = np.mean(data['reward_history'][-100:]) if total_steps >= 100 else np.mean(data['reward_history'])
    max_reward = np.max(data['reward_history'])
    avg_efficiency = np.mean(data['efficiency_history'])
    max_efficiency = np.max(data['efficiency_history'])
    avg_ripple = np.mean(data['ripple_history'])
    min_ripple = np.min(data['ripple_history'])
    
    # 约束满足情况
    ripple_satisfied = np.sum(np.array(data['ripple_history']) <= VisualizationConfig.RIPPLE_THRESHOLD)
    efficiency_satisfied = np.sum(np.array(data['efficiency_history']) >= 0.9)
    both_satisfied = np.sum((np.array(data['ripple_history']) <= VisualizationConfig.RIPPLE_THRESHOLD) & 
                           (np.array(data['efficiency_history']) >= 0.9))
    
    # 最优参数（若存在）
    best = find_best_design(data)
    best_block = "未找到满足约束的最优设计" if best is None else "\n".join(
        [
            "最优参数设计:",
            "- 奖励: {:.2f}".format(best[3]),
            "- 效率: {:.4f} ({:.2f}%)".format(best[1], best[1]*100),
            "- 纹波: {:.4f} ({:.2f}%)".format(best[2], best[2]*100),
            f"- f(Hz): {VisualizationConfig.FIXED_FREQUENCY:.6g}",
        ] + [f"- {name}: {val:.6g}" for name, val in zip(VisualizationConfig.PARAM_NAMES, best[0][1:])]
    )

    # 生成报告
    report = f"""
 Buck变换器PPO训练摘要报告
 {'='*50}

 训练统计:
    总训练步数: {total_steps:,}
    最终平均奖励: {final_reward:.2f}
    最高奖励: {max_reward:.2f}

 性能指标:
    平均效率: {avg_efficiency:.4f} ({avg_efficiency*100:.2f}%)
    最高效率: {max_efficiency:.4f} ({max_efficiency*100:.2f}%)
    平均纹波: {avg_ripple:.4f} ({avg_ripple*100:.2f}%)
    最低纹波: {min_ripple:.4f} ({min_ripple*100:.2f}%)

 约束满足情况:
    纹波约束满足: {ripple_satisfied}/{total_steps} ({ripple_satisfied/total_steps*100:.1f}%)
    效率约束满足: {efficiency_satisfied}/{total_steps} ({efficiency_satisfied/total_steps*100:.1f}%)
    双重约束满足: {both_satisfied}/{total_steps} ({both_satisfied/total_steps*100:.1f}%)

 训练质量评估:
   {'优秀' if final_reward > 10 and both_satisfied/total_steps > 0.1 else '良好' if final_reward > 5 else '需要改进'}

{best_block}
"""
    
    print(report)
    
    # 保存报告
    save_path = os.path.join(VisualizationConfig.SAVE_DIR, 'training_summary.txt')
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✓ 训练摘要报告已保存: {save_path},是否打开训练摘要报告？(y/n):")
    return save_path

"""主程序入口"""
def main():
    print("🚀 Buck变换器PPO训练结果可视化分析")
    print("="*60)
    
    # 加载训练数据
    data = load_training_data()
    if data is None:
        return
    
    # 创建保存目录
    os.makedirs(VisualizationConfig.SAVE_DIR, exist_ok=True)
    
    # 生成各种可视化图表
    plot_training_overview(data)
    plot_performance_analysis(data)
    
    # 分析最优设计
    analyze_optimal_designs(data)
    
    # 生成摘要报告
    summary_path = generate_summary_report(data)
    # Web与本地运行模式适配
    run_mode = os.environ.get('WEB_RUN_MODE', '').lower()  # web: 非阻塞提示；其他：阻塞input
    if run_mode == 'web':
        # 仅提示，由前端通过 /api/run/input 发送 y/n
        print("打开训练摘要报告成功！", flush=True)
        # 前端发送后，另一个进程无法直接回调，因此这里仅在本脚本结束前等待短暂时间，供用户输入
        try:
            # 轻量等待，允许用户通过前端输入框发送一次 y/n
            import time
            time.sleep(2)
        except Exception:
            pass
    else:
        try:
            choice = input("打开训练摘要报告成功！").strip().lower()
        except Exception:
            choice = 'n'
        if choice == 'y':
            # 解析桌面路径
            desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
            target_dir = os.path.join(desktop, 'AI_Training_Summary')
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, os.path.basename(summary_path))
            try:
                shutil.copyfile(summary_path, target_path)
                print(f"\n✓ 已复制报告到桌面: {target_path}")
            except Exception as e:
                print(f"⚠️ 复制到桌面失败，将直接打开原文件: {e}")
                target_path = summary_path
            # 打开文件
            try:
                if sys.platform.startswith('win'):
                    os.startfile(target_path)  # type: ignore[attr-defined]
                elif sys.platform == 'darwin':
                    subprocess.Popen(['open', target_path])
                else:
                    subprocess.Popen(['xdg-open', target_path])
            except Exception as e:
                print(f"⚠️ 打开报告失败: {e}")
    
    print("\n✅ 可视化分析完成！")
    print(f"📁 结果保存在: {VisualizationConfig.SAVE_DIR}")

if __name__ == '__main__':
    main()
