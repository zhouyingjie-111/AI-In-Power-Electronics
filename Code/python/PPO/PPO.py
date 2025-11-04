"""
PPO强化学习优化Buck变换器参数设计
=====================================

本模块使用PPO算法优化Buck变换器的关键参数,通过强化学习寻找最优的设计参数组合。
主要功能：
1. 定义Buck变换器设计参数的强化学习环境
2. 使用预训练的代理模型预测性能指标
3. 通过PPO算法优化参数,最大化效率同时满足纹波约束
4. 提供训练过程监控和结果可视化

"""

import numpy as np
import pandas as pd
import os
import sys
import random
import math
from typing import Tuple, Dict, List, Optional

# Force UTF-8 stdout/stderr to avoid UnicodeEncodeError on Windows GBK consoles
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:
    try:
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        os.environ.setdefault("PYTHONUTF8", "1")
    except Exception:
        pass
os.environ.setdefault('TF_CPP_MIN_LOG_LEVEL', '3')	# 仅显示ERROR，且不覆盖外部已设置
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor, VecNormalize
from stable_baselines3.common.callbacks import EvalCallback, BaseCallback
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm

"""设置字体支持"""
def setup_chinese_font():

    try:
        # 尝试设置中文字体
        font_candidates = [
            'SimHei',           # Windows 黑体
            'Microsoft YaHei',  # Windows 微软雅黑
            'WenQuanYi Micro Hei',  # Linux 文泉驿微米黑
            'PingFang SC',      # macOS 苹方
            'Hiragino Sans GB', # macOS 冬青黑体
            'Arial Unicode MS', # 通用
            'DejaVu Sans'       # 备用
        ]
        
        # 获取系统可用字体
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 找到第一个可用的中文字体
        chinese_font = None
        for font in font_candidates:
            if font in available_fonts:
                chinese_font = font
                break
        
        if chinese_font:
            matplotlib.rcParams['font.sans-serif'] = [chinese_font] + font_candidates
        else:
            # 如果没有找到中文字体，使用英文标签
            matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
            print("⚠️ 未找到中文字体，将使用英文标签")
            
        matplotlib.rcParams['axes.unicode_minus'] = False
        
    except Exception as e:
        print(f"⚠️ 字体设置失败: {e}")
        # 使用默认设置
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
        matplotlib.rcParams['axes.unicode_minus'] = False

# 设置中文字体
setup_chinese_font()

# 禁用matplotlib警告
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

"""
PPO训练配置,集中管理所有关键参数
"""
# 配置参数与模型加载
class Config:

    # 文件路径配置
    MODEL_PATH = 'E:/AI-based optimized design/Trained_model/trainedNet.keras'
    X_SCALER_PATH = 'E:/AI-based optimized design/Data/Input_Data/x_scaled_data.csv'
    Y_SCALER_PATH = 'E:/AI-based optimized design/Data/Input_Data/y_scaled_data.csv'
    HISTORY_PATH = 'E:/AI-based optimized design/Data/Training_History/training_history.npz'
    TENSORBOARD_LOG = "E:/AI-based optimized design/TensorBoard/PPO_Buck/"
    MODEL_SAVE_PATH = 'E:/AI-based optimized design/Trained_model/'
    CHECKPOINT_PATH = 'E:/AI-based optimized design/Trained_model/checkpoints/'
    VECNORM_PATH = 'E:/AI-based optimized design/Trained_model/vecnormalize.pkl'
    
    # 交错并联Buck变换器参数设计范围
    FIXED_FREQUENCY = 500e3         # 固定开关频率 (Hz)
    PARAM_BOUNDS = {
        'L(H)': (1e-6, 3e-6),       # 电感 (H)
        'C(F)': (8e-6, 10e-6),      # 电容 (F)
        'Ron': (0.002, 0.005),         # 开关管导通电阻 (Ω)
        'RL': (0.0015, 0.1),          # 电感等效串联电阻 (Ω)
        'RC': (0.01, 0.2)           # 电容等效串联电阻 (Ω)
    }
    
    # 性能约束
    RIPPLE_THRESHOLD = 0.005         # 纹波系数上限（0.5%）
    MIN_EFFICIENCY = 0.75           # 最低效率要求
    MAX_EFFICIENCY = 0.98           # 最高效率限制
    
    # PPO算法参数（优化版）
    PPO_CONFIG = {
        'learning_rate': 5e-4,      # 提高学习率，加快收敛
        'n_steps': 2048,            # 每次更新收集的步数
        'batch_size': 256,          # 适中批次，平衡速度和稳定性
        'n_epochs': 15,             # 增加训练轮数，提高样本利用率
        'gamma': 0.99,              # 折扣因子
        'gae_lambda': 0.95,         # GAE参数
        'clip_range': 0.2,          # 裁剪范围
        'ent_coef': 0.005,          # 降低熵系数，加快收敛
        'vf_coef': 0.5,             # 价值函数系数
        'max_grad_norm': 0.5        # 梯度裁剪阈值
    }
    
    # 训练配置（优化版）
    MAX_STEPS_PER_EPISODE = 50      # 每个episode最大步数
    EXPLORATION_RATE = 0.0          # 禁用环境级随机探索（由策略负责）
    SAVE_FREQUENCY = 100            # 历史保存频率
    EVAL_FREQUENCY = 1024           # 提高评估频率，更快发现好模型
    CHECKPOINT_FREQUENCY = 2048     # 检查点保存频率

"""
加载预训练的代理模型和标准化器
    
返回: Tuple[代理模型, 输入标准化器, 输出标准化器]
"""
def load_surrogate_model() -> Tuple[object, StandardScaler, StandardScaler]:

    print("正在加载代理模型和标准化器...")
    
    # 加载预训练的神经网络模型
    surrogate_model = load_model(Config.MODEL_PATH)
    print(f"✓ 代理模型已加载: {Config.MODEL_PATH}")
    
    # 加载输入标准化参数
    x_scaler_params = pd.read_csv(Config.X_SCALER_PATH)
    scaler_x = StandardScaler()
    scaler_x.mean_ = x_scaler_params['x_mu'].values
    scaler_x.scale_ = x_scaler_params['x_sigma'].values
    scaler_x.var_ = scaler_x.scale_ ** 2
    print(f"✓ 输入标准化器已加载: {Config.X_SCALER_PATH}")
    
    # 加载输出标准化参数
    y_scaler_params = pd.read_csv(Config.Y_SCALER_PATH)
    scaler_y = StandardScaler()
    scaler_y.mean_ = y_scaler_params['y_mu'].values
    scaler_y.scale_ = y_scaler_params['y_sigma'].values
    scaler_y.var_ = scaler_y.scale_ ** 2
    print(f"✓ 输出标准化器已加载: {Config.Y_SCALER_PATH}")
    
    return surrogate_model, scaler_x, scaler_y

# 加载模型和标准化器
surrogate_model, scaler_x, scaler_y = load_surrogate_model()

"""
Buck变换器设计优化强化学习环境
	
该环境将Buck变换器的设计参数优化问题转化为强化学习问题:
- 状态空间:6个设计参数 + 2个性能指标(纹波、效率)
- 动作空间:6维连续动作,范围[-1, 1]，映射到实际参数范围
- 奖励函数：基于效率最大化、纹波约束满足、参数多样性
    
关键特性：
1. 使用预训练代理模型快速预测性能指标
2. 多目标奖励函数平衡效率与约束
3. 历史记录支持训练过程分析
4. 物理约束确保设计参数合理性
"""
# Buck变换器强化学习环境搭建
class BuckConverterEnv(gym.Env):

	def __init__(self, track_history: bool = True):
		super(BuckConverterEnv, self).__init__()
		self.track_history = track_history
		
		# 固定频率
		self.fixed_frequency = Config.FIXED_FREQUENCY
		
		# 动作空间：5维连续动作（移除频率），范围[-1, 1]
		self.action_space = spaces.Box(
			low=np.float32(np.array([-1.0] * 5)),
			high=np.float32(np.array([1.0] * 5)),
			dtype=np.float32
		)
		
		# 观测空间：7维连续状态 
		# 前5维：设计参数 [L, C, Ron, RL, RC];后2维：性能指标 [ripple, efficiency]
		self.observation_space = spaces.Box(
			low=np.float32(-np.inf),
			high=np.float32(np.inf),
			shape=(7,),
			dtype=np.float32
		)

		# 参数边界和名称
		self.param_bounds = np.array(list(Config.PARAM_BOUNDS.values()))
		self.param_names = list(Config.PARAM_BOUNDS.keys())
		self.param_ranges = self.param_bounds[:, 1] - self.param_bounds[:, 0]
		
		# 性能约束
		self.ripple_threshold = Config.RIPPLE_THRESHOLD
		self.min_efficiency = Config.MIN_EFFICIENCY
		self.max_efficiency = Config.MAX_EFFICIENCY
		
		# Episode控制
		self.max_steps = Config.MAX_STEPS_PER_EPISODE
		self.current_step = 0

		# 历史记录初始化（始终具备属性，是否读写由 track_history 控制）
		self.history_file = Config.HISTORY_PATH
		# 先初始化为空，确保属性存在
		self.param_history = []
		self.ripple_history = []
		self.efficiency_history = []
		self.reward_history = []
		self.diversity_history = []
		self.boundary_distance_history = []
		self.step_count = 0
		# 仅在训练环境时加载历史
		if self.track_history:
			os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
			self.load_history()

	# 加载训练历史
	def load_history(self):
		try:
			if os.path.exists(self.history_file):
				data = np.load(self.history_file)
				self.param_history = list(data['param_history'])
				self.ripple_history = list(data['ripple_history'])
				self.efficiency_history = list(data['efficiency_history'])
				self.reward_history = list(data['reward_history'])
				self.diversity_history = list(data['diversity_history'])
				self.boundary_distance_history = list(data['boundary_distance_history'])
				self.step_count = len(self.reward_history)
				print(f"✓ 已加载训练历史，共 {self.step_count} 步")
			else:
				self.clear_history()
		except Exception as e:
			print(f"✗ 加载历史记录失败: {e}")
			self.clear_history()
	# 保存训练历史记录
	def save_history(self, verbose: bool = False):
	
		try:
			if not self.track_history:
				return
			np.savez(
				self.history_file,
				param_history=np.array(self.param_history),
				ripple_history=np.array(self.ripple_history),
				efficiency_history=np.array(self.efficiency_history),
				reward_history=np.array(self.reward_history),
				diversity_history=np.array(self.diversity_history),
				boundary_distance_history=np.array(self.boundary_distance_history)
			)
			# 只在 verbose=True 时打印
			if verbose:
				print(f"✓ 已保存训练历史（总步数: {self.step_count}）")
		except Exception as e:
			print(f"✗ 保存历史记录失败: {e}")

	#清空训练历史trained_steps
	def clear_history(self):
		self.param_history = []
		self.ripple_history = []
		self.efficiency_history = []
		self.reward_history = []
		self.diversity_history = []
		self.boundary_distance_history = []
		self.step_count = 0
		if self.track_history:
			print("✓ 已清空训练历史")

	# ========== 核心工具函数 ==========
	"""
	将动作空间[-1, 1]映射到实际参数范围
		
	参数:action: 5维动作向量,范围[-1, 1]（不包含频率）
			
	返回:6维参数向量,包含固定频率和5个可变参数 [f, L, C, Ron, RL, RC]
		"""
	def scale_action_to_params(self, action: np.ndarray) -> np.ndarray:
		# 将5维动作映射到实际参数范围
		params_without_freq = self.param_bounds[:, 0] + (action + 1) * 0.5 * self.param_ranges
		# 在最前面添加固定频率
		return np.concatenate([[self.fixed_frequency], params_without_freq])

	"""
	使用代理模型预测Buck变换器性能指标
		
	参数:params: 6维参数向量 [f, L, C, Ron, RL, RC]
			
	返回:Tuple[纹波系数, 效率]
	"""
	def predict_performance(self, params: np.ndarray) -> Tuple[float, float]:
		# 标准化输入参数
		params_scaled = scaler_x.transform(params.reshape(1, -1))
		
		# 使用代理模型预测
		pred_scaled = surrogate_model.predict(params_scaled, verbose=0)
		
		# 反标准化输出结果
		ripple, efficiency = scaler_y.inverse_transform(pred_scaled)[0]
		
		return ripple, efficiency

	# 环境交互核心 
	"""
	执行一步环境交互
		
	参数:action: 5维动作向量,范围[-1, 1]（不包含频率）
			
	返回:Tuple[新状态, 奖励, 是否终止, 是否截断, 信息字典]
	"""
	def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
		self.current_step += 1
		
		# 探索策略：随机探索增强多样性
		if random.random() < Config.EXPLORATION_RATE:
			action = np.random.uniform(-1, 1, size=5)

		# 动作映射到实际参数（包含固定频率）
		params = self.scale_action_to_params(action)
		
		# 使用代理模型预测性能
		ripple, efficiency = self.predict_performance(params)

		# 物理约束检查和裁剪
		physical_violation = self._check_physical_constraints(efficiency, ripple)
		efficiency = np.clip(efficiency, self.min_efficiency, self.max_efficiency)
		ripple = np.clip(ripple, 0, 0.06)

		# 计算多目标奖励函数
		reward = self._calculate_reward(params, ripple, efficiency, physical_violation)

		# 更新状态和历史记录（状态不包含固定频率）
		self.state = np.concatenate([params[1:], [ripple, efficiency]])
		self._update_history(params, ripple, efficiency, reward)

		# 定期保存历史（仅训练环境，静默保存）
		if self.track_history and self.step_count % Config.SAVE_FREQUENCY == 0:
			self.save_history(verbose=False)

		# Episode终止条件
		terminated = False
		truncated = self.current_step >= self.max_steps
		
		# 构建信息字典
		info = self._build_info_dict(params, ripple, efficiency, reward, physical_violation)
		
		return self.state, reward, terminated, truncated, info

	"""检查物理约束是否违反"""
	def _check_physical_constraints(self, efficiency: float, ripple: float) -> bool:
	
		return (efficiency < self.min_efficiency or efficiency > self.max_efficiency or
				ripple < 0 or ripple > 0.06)

	"""
	计算多目标奖励函数（优化版）
		
	奖励组成：
	1. 效率奖励：鼓励高效率设计（权重加大）
	2. 纹波惩罚：惩罚超出约束的纹波（权重加大）
	3. 边界奖励：鼓励参数远离边界
	4. 多样性奖励：鼓励参数多样性
	"""
	def _calculate_reward(self, params: np.ndarray, ripple: float, efficiency: float, 
						 physical_violation: bool) -> float:
		# 1. 效率奖励（主要目标，权重加大）
		eff_reward = 150 * (efficiency - 0.85)  # 基准效率85%，权重从100提高到150
		
		# 效率等级奖励（增强激励）
		if efficiency >= 0.96:
			eff_reward += 30  # 优秀效率（从20提高到30）
		elif efficiency >= 0.93:
			eff_reward += 15  # 良好效率（从10提高到15）
		elif efficiency >= 0.90:
			eff_reward += 8   # 可接受效率（从5提高到8）

		# 2. 纹波惩罚（权重加大，更严格）
		ripple_penalty = 0.0
		if ripple > self.ripple_threshold:
			ripple_excess = (ripple - self.ripple_threshold) / self.ripple_threshold
			ripple_penalty = -3.0 * np.log(1 + ripple_excess)  # 权重从-1.5提高到-3.0

		# 3. 边界距离奖励（避免参数在边界附近，仅考虑可变参数）
		# params[0]是固定频率，从索引1开始是可变参数
		min_dist = min(
			min((params[i+1] - self.param_bounds[i, 0]) / self.param_ranges[i],
				(self.param_bounds[i, 1] - params[i+1]) / self.param_ranges[i])
			for i in range(len(self.param_bounds))
		)
		boundary_reward = 1.0 * min_dist if min_dist > 0.2 else 0.0

		# 4. 多样性奖励（鼓励参数探索）
		diversity_bonus = self._calculate_diversity_bonus(params)

		# 物理约束违反惩罚（加大惩罚）
		if physical_violation:
			return -15.0  # 从-10.0提高到-15.0
		else:
			return eff_reward + ripple_penalty + boundary_reward + diversity_bonus

	"""计算多样性奖励"""
	def _calculate_diversity_bonus(self, params: np.ndarray) -> float:
		# 评估环境或历史过短时，不计算多样性奖励
		if (not self.track_history) or (not self.param_history) or (len(self.param_history) < 5):
			return 0.0
			
		# 与最近5个参数的平均差异（仅比较可变参数，跳过固定频率）
		recent_history = np.array(self.param_history[-5:])
		avg_params = np.mean(recent_history, axis=0)
		# 只比较可变参数（索引1-5），跳过固定频率（索引0）
		param_diff = np.abs(params[1:] - avg_params[1:]) / self.param_ranges
		diversity_bonus = min(np.mean(param_diff) * 2.0, 2.0)
		
		return diversity_bonus

	"""更新训练历史记录"""
	def _update_history(self, params: np.ndarray, ripple: float, 
					   efficiency: float, reward: float):
		if self.track_history:
			self.param_history.append(params)
			self.ripple_history.append(ripple)
			self.efficiency_history.append(efficiency)
			self.reward_history.append(reward)
		
		# 计算边界距离（params[0]是固定频率，从索引1开始是可变参数）
		min_dist = min(
			min((params[i+1] - self.param_bounds[i, 0]) / self.param_ranges[i],
				(self.param_bounds[i, 1] - params[i+1]) / self.param_ranges[i])
			for i in range(len(self.param_bounds))
		)
		if self.track_history:
			self.boundary_distance_history.append(min_dist)
		
		# 计算多样性奖励
		diversity_bonus = self._calculate_diversity_bonus(params)
		if self.track_history:
			self.diversity_history.append(diversity_bonus)
		
		self.step_count += 1
		
	"""构建信息字典"""
	def _build_info_dict(self, params: np.ndarray, ripple: float, efficiency: float,
						reward: float, physical_violation: bool) -> Dict:
		return {
			'params': params,
			'ripple': ripple,
			'efficiency': efficiency,
			'reward': reward,
			'ripple_violation': ripple > self.ripple_threshold,
			'physical_violation': physical_violation,
			'step': self.current_step,
			'total_steps': self.step_count
		}

	"""
	重置环境到初始状态
		
	参数:seed: 随机种子
		options: 重置选项
			
	返回:Tuple[初始状态, 信息字典]
	"""
	def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:

		# 设置随机种子
		if seed is not None:
			np.random.seed(seed)
			random.seed(seed)

		# 重置episode计数器
		self.current_step = 0

		# 在合理范围内随机初始化参数（不包含频率）
		# 选择参数范围的中心区域，避免边界效应
		random_params = [
			self.fixed_frequency,              # 开关频率：固定500kHz
			np.random.uniform(1.2e-6, 1.8e-6), # 电感：中心区域
			np.random.uniform(8.5e-6, 9.5e-6), # 电容：中心区域
			np.random.uniform(0.02, 0.06),     # 开关管电阻：中心区域
			np.random.uniform(0.02, 0.06),     # 电感电阻：中心区域
			np.random.uniform(0.03, 0.08)      # 电容电阻：中心区域
		]
		
		# 预测初始性能
		ripple, efficiency = self.predict_performance(np.array(random_params))
		
		# 构建初始状态（不包含固定频率，只包含5个可变参数和2个性能指标）
		self.state = np.concatenate([random_params[1:], [ripple, efficiency]])
		
		return self.state, {}

	"""
	渲染当前环境状态
		
	参数:mode: 渲染模式
			
	返回:渲染结果(文本模式返回字符串,其他模式返回None)
	"""
	def render(self, mode: str = 'human') -> Optional[str]:

		if mode == 'human':
			params_without_freq = self.state[:5]
			ripple, efficiency = self.state[5:]
			
			print("\n" + "="*50)
			print("           Buck变换器设计状态")
			print("="*50)
			print(f"Episode步数: {self.current_step}/{self.max_steps}")
			print(f"总训练步数: {self.step_count}")
			print("\n设计参数:")
			print(f"  {'f(Hz)':>8}: {self.fixed_frequency:>12.6g}")
			for name, value in zip(self.param_names, params_without_freq):
				print(f"  {name:>8}: {value:>12.6g}")
			
			print(f"\n性能指标:")
			print(f"  纹波系数: {ripple:>8.4f} ({'✓ 满足约束' if ripple <= self.ripple_threshold else '✗ 超出约束'})")
			print(f"  效率:     {efficiency:>8.4f} ({efficiency * 100:>6.2f}%)")
			print("="*50)
			
		return None

"""
创建并配置PPO模型
	
参数:env: Buck变换器强化学习环境
		
返回:配置好的PPO模型
"""
# PPO模型配置与训练设置
def create_ppo_model(env) -> PPO:

	print("正在创建PPO模型...")
	
	# 创建TensorBoard日志目录
	os.makedirs(Config.TENSORBOARD_LOG, exist_ok=True)
	
	# 创建PPO模型
	model = PPO(
		"MlpPolicy",                    # 使用多层感知机策略
		env,                            # 环境（已监控/归一化）
		verbose=1,                      # 显示训练进度
		tensorboard_log=Config.TENSORBOARD_LOG,  # TensorBoard日志
		**Config.PPO_CONFIG             # 使用配置中的超参数
	)
	
	print("✓ PPO模型创建完成")
	print(f"  学习率: {Config.PPO_CONFIG['learning_rate']}")
	print(f"  批大小: {Config.PPO_CONFIG['batch_size']}")
	print(f"  更新步数: {Config.PPO_CONFIG['n_steps']}")
	print(f"  训练轮数: {Config.PPO_CONFIG['n_epochs']}")
	
	return model

"""
创建训练回调函数
	
返回:回调函数列表
"""
def create_training_callbacks() -> List[BaseCallback]:

	callbacks = []
	
	# 确保保存与日志目录存在
	os.makedirs(Config.MODEL_SAVE_PATH, exist_ok=True)
	os.makedirs(Config.CHECKPOINT_PATH, exist_ok=True)
	os.makedirs(os.path.join(Config.TENSORBOARD_LOG, 'Eval/'), exist_ok=True)

	# 1. 评估回调 - 定期评估并保存最佳模型
	eval_callback = EvalCallback(
		VecMonitor(load_or_create_vec_env(training=False, track_history=False)),
		best_model_save_path=Config.MODEL_SAVE_PATH,
		log_path=os.path.join(Config.TENSORBOARD_LOG, 'Eval/'),
		eval_freq=Config.EVAL_FREQUENCY,
		deterministic=False,
		verbose=1
	)
	callbacks.append(eval_callback)
	
	# 2. 检查点回调 - 定期保存模型检查点
	checkpoint_callback = CheckpointCallback(
		save_freq=Config.CHECKPOINT_FREQUENCY,
		save_path=Config.CHECKPOINT_PATH,
		name_prefix="buck_ppo"
	)
	callbacks.append(checkpoint_callback)
	
	print("✓ 训练回调函数创建完成")
	return callbacks

def make_base_env(track_history: bool = True) -> DummyVecEnv:
	return DummyVecEnv([lambda: BuckConverterEnv(track_history=track_history)])

def load_or_create_vec_env(training: bool = True, track_history: bool = True) -> VecNormalize:
	"""创建或加载带归一化的环境"""
	base_env = make_base_env(track_history=track_history)
	if os.path.exists(Config.VECNORM_PATH):
		try:
			vec_env = VecNormalize.load(Config.VECNORM_PATH, base_env)
			vec_env.training = training
			vec_env.norm_reward = True
			vec_env.norm_obs = True
			print(f"✓ 已加载VecNormalize统计: {Config.VECNORM_PATH} (training={training})")
			return vec_env
		except Exception as e:
			# 检查是否是观测空间不匹配
			if "observation_space" in str(e).lower() or "shape" in str(e).lower():
				print(f"⚠️ VecNormalize与当前环境不兼容（观测空间已更改）")
				print(f"⚠️ 将备份旧文件并创建新的VecNormalize")
				# 备份旧文件
				import shutil
				import time
				timestamp = time.strftime("%Y%m%d_%H%M%S")
				backup_path = Config.VECNORM_PATH.replace('.pkl', f'_backup_{timestamp}.pkl')
				try:
					shutil.move(Config.VECNORM_PATH, backup_path)
					print(f"✓ 旧VecNormalize已备份到: {backup_path}")
				except Exception as backup_error:
					print(f"⚠️ 备份失败: {backup_error}")
			else:
				print(f"✗ 加载VecNormalize失败，使用新统计: {e}")
	# 新建
	vec_env = VecNormalize(
		base_env,
		norm_obs=True,
		norm_reward=True,
		clip_obs=10.0,
		clip_reward=10.0
	)
	vec_env.training = training
	print("✓ 已创建新的VecNormalize环境")
	return vec_env

def get_inner_env(vec_env) -> BuckConverterEnv:
	"""获取最内层的 BuckConverterEnv 实例 (第0个子环境)"""
	e = vec_env
	# 解包 VecEnvWrapper 链
	while hasattr(e, 'venv'):
		e = e.venv
	# 取第一个子环境
	if hasattr(e, 'envs') and len(e.envs) > 0:
		return e.envs[0]
	return e

# 检查点回调类定义
"""
定期保存模型检查点的回调函数
"""
class CheckpointCallback(BaseCallback):

	"""
	初始化检查点回调
		
	参数:save_freq: 保存频率（步数）
		save_path: 保存路径
		name_prefix: 文件名前缀
	"""
	def __init__(self, save_freq: int, save_path: str, name_prefix: str = "ppo_model"):

		super(CheckpointCallback, self).__init__()
		self.save_freq = save_freq
		self.save_path = save_path
		self.name_prefix = name_prefix
	
	"""初始化回调，创建保存目录"""
	def _init_callback(self) -> None:
		if self.save_path is not None:
			os.makedirs(self.save_path, exist_ok=True)
	
	"""每步检查是否需要保存检查点"""
	def _on_step(self) -> bool:
		if self.n_calls % self.save_freq == 0:
			path = os.path.join(self.save_path, f"{self.name_prefix}_{self.num_timesteps}_steps")
			self.model.save(path)
			print(f"✓ 检查点已保存: 步数 {self.num_timesteps} -> {path}")
		return True

# 创建环境（带VecNormalize与监控）与回调
print("正在初始化训练环境...")
try:
	env = load_or_create_vec_env(training=True, track_history=True)
	env = VecMonitor(env)
	print("✓ Buck变换器环境创建完成 (VecNormalize)")
except Exception as e:
	print(f"❌ 环境创建失败: {e}")
	import traceback
	traceback.print_exc()
	raise

# 创建训练回调
callbacks = create_training_callbacks()

# 训练过程可视化
"""
绘制训练进度关键指标
	
参数:env: Buck变换器环境(包含历史数据)
	save_dir: 图片保存目录
"""
def plot_training_progress(env: BuckConverterEnv, save_dir: str = "E:/AI-based optimized design/Visualization/") -> None:

	os.makedirs(save_dir, exist_ok=True)
	
	if not env.reward_history:
		print("⚠️ 没有训练历史数据，跳过可视化")
		return
	
	print("正在生成训练进度可视化...")
	
	# 创建图形
	fig, axes = plt.subplots(2, 2, figsize=(12, 10))
	fig.suptitle('Buck变换器PPO训练进度', fontsize=16, fontweight='bold')
	
	# 1. 奖励曲线
	axes[0, 0].plot(env.reward_history, alpha=0.7, linewidth=1)
	axes[0, 0].set_title('训练奖励变化')
	axes[0, 0].set_xlabel('训练步数')
	axes[0, 0].set_ylabel('奖励值')
	axes[0, 0].grid(True, alpha=0.3)
	
	# 2. 效率变化
	axes[0, 1].plot(env.efficiency_history, alpha=0.7, linewidth=1, color='green')
	axes[0, 1].axhline(y=0.95, color='red', linestyle='--', alpha=0.7, label='目标效率 95%')
	axes[0, 1].set_title('效率变化')
	axes[0, 1].set_xlabel('训练步数')
	axes[0, 1].set_ylabel('效率')
	axes[0, 1].legend()
	axes[0, 1].grid(True, alpha=0.3)
	
	# 3. 纹波变化
	axes[1, 0].plot(env.ripple_history, alpha=0.7, linewidth=1, color='orange')
	axes[1, 0].axhline(y=Config.RIPPLE_THRESHOLD, color='red', linestyle='--', alpha=0.7, label='纹波阈值 2%')
	axes[1, 0].set_title('纹波系数变化')
	axes[1, 0].set_xlabel('训练步数')
	axes[1, 0].set_ylabel('纹波系数')
	axes[1, 0].legend()
	axes[1, 0].grid(True, alpha=0.3)
	
	# 4. 效率vs纹波散点图
	scatter = axes[1, 1].scatter(env.efficiency_history, env.ripple_history, 
								 c=env.reward_history, cmap='viridis', alpha=0.6)
	axes[1, 1].axhline(y=Config.RIPPLE_THRESHOLD, color='red', linestyle='--', alpha=0.7, label='纹波阈值')
	axes[1, 1].axvline(x=0.95, color='green', linestyle='--', alpha=0.7, label='目标效率')
	axes[1, 1].set_title('效率 vs 纹波 (颜色=奖励)')
	axes[1, 1].set_xlabel('效率')
	axes[1, 1].set_ylabel('纹波系数')
	axes[1, 1].legend()
	axes[1, 1].grid(True, alpha=0.3)
	plt.colorbar(scatter, ax=axes[1, 1], label='奖励值')
	
	plt.tight_layout()
	
	# 保存图片
	save_path = os.path.join(save_dir, 'training_progress.png')
	plt.savefig(save_path, dpi=300, bbox_inches='tight')
	plt.close()
	
	print(f"✓ 训练进度图已保存: {save_path}")

# def plot_parameter_evolution(env: BuckConverterEnv, save_dir: str = "E:/AI-based optimized design/Visualization/") -> None:
# 	"""
# 	绘制参数演化过程
	
# 	Args:
# 		env: Buck变换器环境
# 		save_dir: 图片保存目录
# 	"""
# 	if not env.param_history:
# 		print("⚠️ 没有参数历史数据，跳过参数演化图")
# 		return
	
# 	print("正在生成参数演化图...")
	
# 	param_history = np.array(env.param_history)
# 	param_names = list(Config.PARAM_BOUNDS.keys())
	
# 	fig, axes = plt.subplots(2, 3, figsize=(15, 10))
# 	fig.suptitle('Buck变换器参数演化过程', fontsize=16, fontweight='bold')
# 	axes = axes.flatten()
	
# 	for i, (name, bounds) in enumerate(Config.PARAM_BOUNDS.items()):
# 		ax = axes[i]
# 		ax.plot(param_history[:, i], alpha=0.7, linewidth=1)
# 		ax.axhline(y=bounds[0], color='red', linestyle='--', alpha=0.5, label='下界')
# 		ax.axhline(y=bounds[1], color='red', linestyle='--', alpha=0.5, label='上界')
# 		ax.set_title(f'{name} 演化')
# 		ax.set_xlabel('训练步数')
# 		ax.set_ylabel('参数值')
# 		ax.legend()
# 		ax.grid(True, alpha=0.3)
	
# 	plt.tight_layout()
	
# 	# 保存图片
# 	save_path = os.path.join(save_dir, 'parameter_evolution.png')
# 	plt.savefig(save_path, dpi=300, bbox_inches='tight')
# 	plt.close()
	
# 	print(f"✓ 参数演化图已保存: {save_path}")

# 训练主流程
"""
PPO模型训练主函数
	
参数:total_timesteps: 总训练步数
	batch_size: 每批训练步数
		
返回:训练奖励历史
"""
def train_ppo_model(total_timesteps: int = 36000, batch_size: int = 4096) -> List[float]:

	print("开始PPO训练")
	print("="*60)
	
	# 模型路径配置
	ppo_model_path = os.path.join(Config.MODEL_SAVE_PATH, 'buck_optimizer_ppo')
	checkpoint_path = ppo_model_path + '_checkpoint'
	
	# 检查是否存在检查点
	if os.path.exists(checkpoint_path + '.zip'):
		print(f"✓ 发现检查点: {checkpoint_path}")
		try:
			# 尝试加载检查点
			model = PPO.load(checkpoint_path, env=env)
			model.verbose = 1  # 设置为显示训练信息
			trained_steps = model.num_timesteps
			print(f"✓ 已恢复训练，当前步数: {trained_steps}")
		except (ValueError, AssertionError) as e:
			# 观测空间或动作空间不匹配（版本升级导致）
			if "spaces do not match" in str(e) or "observation_space" in str(e):
				print(f"⚠️ 检查点与当前环境不兼容（观测空间已更改）")
				print(f"⚠️ 将备份旧检查点并开始全新训练")
				
				# 备份旧文件
				import shutil
				import time
				timestamp = time.strftime("%Y%m%d_%H%M%S")
				backup_dir = os.path.join(Config.CHECKPOINT_PATH, f'backup_{timestamp}')
				os.makedirs(backup_dir, exist_ok=True)
				
				if os.path.exists(checkpoint_path + '.zip'):
					shutil.move(checkpoint_path + '.zip', 
							   os.path.join(backup_dir, 'buck_optimizer_ppo_checkpoint.zip'))
					print(f"✓ 旧检查点已备份到: {backup_dir}")
				
				if os.path.exists(Config.VECNORM_PATH):
					shutil.move(Config.VECNORM_PATH, 
							   os.path.join(backup_dir, 'vecnormalize.pkl'))
					print(f"✓ 旧VecNormalize已备份")
				
				# 开始全新训练
				model = create_ppo_model(env)
				trained_steps = 0
				# 清空底层环境历史
				try:
					inner_env = get_inner_env(env)
					inner_env.clear_history()
					print("✓ 已清空训练历史，开始全新训练")
				except Exception as e:
					print(f"⚠️ 无法清空历史(非致命): {e}")
			else:
				# 其他错误，重新抛出
				raise
	else:
		print("✓ 开始全新训练会话")
		model = create_ppo_model(env)
		trained_steps = 0
		# 清空底层环境历史
		try:
			inner_env = get_inner_env(env)
			inner_env.clear_history()
		except Exception as e:
			print(f"⚠️ 无法清空历史(非致命): {e}")

	# 计算训练批次
	remaining_steps = total_timesteps - trained_steps
	if remaining_steps < 0:
		remaining_steps = 0;
	batches = math.ceil(remaining_steps / batch_size)
	
	print(f"训练配置:")
	print(f"  总步数: {total_timesteps}")
	print(f"  批大小: {batch_size}")
	print(f"  剩余步数: {remaining_steps}")
	print(f"  训练批次数: {batches}")
	print("="*60)

	# 分批训练
	for batch in range(batches):
		print(f"\n{'='*60}")
		print(f"🔄 训练批次 {batch+1}/{batches}")
		print(f"   目标步数: {trained_steps} -> {min(trained_steps + batch_size, total_timesteps)}")
		print(f"{'='*60}")

		current_batch_size = min(batch_size, total_timesteps - trained_steps)

		# 执行训练
		print(f"\n开始训练 {current_batch_size} 步...")
		model.learn(
			total_timesteps=current_batch_size,
			callback=callbacks,
			reset_num_timesteps=False,
			tb_log_name="PPO_Buck1",
			progress_bar=True
		)

		trained_steps = model.num_timesteps

		# 显示训练进度统计
		try:
			inner_env = get_inner_env(env)
			if inner_env.reward_history:
				recent_rewards = inner_env.reward_history[-100:]
				recent_efficiency = inner_env.efficiency_history[-100:]
				recent_ripple = inner_env.ripple_history[-100:]
				print(f"\n📊 最近100步统计:")
				print(f"   平均奖励: {np.mean(recent_rewards):>8.2f}")
				print(f"   平均效率: {np.mean(recent_efficiency):>8.4f} ({np.mean(recent_efficiency)*100:.2f}%)")
				print(f"   平均纹波: {np.mean(recent_ripple):>8.4f}")
				print(f"   总训练步数: {inner_env.step_count}")
		except Exception as e:
			pass

		# 保存检查点、VecNormalize统计和历史
		model.save(checkpoint_path)
		try:
			os.makedirs(os.path.dirname(Config.VECNORM_PATH), exist_ok=True)
			env.save(Config.VECNORM_PATH)
		except Exception as e:
			print(f"✗ 保存VecNormalize失败: {e}")
		# 保存底层环境历史（verbose=True 显示保存信息）
		try:
			inner_env = get_inner_env(env)
			inner_env.save_history(verbose=True)
		except Exception as e:
			print(f"⚠️ 无法保存历史(非致命): {e}")
		print(f"✓ 检查点已保存 -> {checkpoint_path}")

	# 训练完成
	print("训练完成")
	print("="*60)
	
	# 保存最终模型与VecNormalize统计
	print("\n保存最终模型...")
	model.save(ppo_model_path)
	try:
		env.save(Config.VECNORM_PATH)
	except Exception as e:
		print(f"✗ 保存最终VecNormalize失败: {e}")
	# 保存底层环境历史
	try:
		inner_env = get_inner_env(env)
		inner_env.save_history(verbose=True)
	except Exception as e:
		print(f"⚠️ 最终保存历史失败(非致命): {e}")
	print(f"✓ 最终模型已保存: {ppo_model_path}")
	
	# 生成可视化
	print("\n📊 生成训练可视化...")
	# 使用底层环境数据进行可视化
	try:
		inner_env = get_inner_env(env)
		plot_training_progress(inner_env)
	except Exception as e:
		print(f"⚠️ 可视化失败(非致命): {e}")
	
	# 返回底层环境的奖励历史
	try:
		inner_env = get_inner_env(env)
		return inner_env.reward_history
	except Exception:
		return []

# 主程序入口
def main():
	print("🚀 Buck变换器PPO优化系统启动")
	print("="*60)
	
	# 显示配置信息
	print("📋 当前配置:")
	print(f"  代理模型: {Config.MODEL_PATH}")
	print(f"  参数范围: {len(Config.PARAM_BOUNDS)} 个参数")
	print(f"  纹波阈值: {Config.RIPPLE_THRESHOLD*100:.1f}%")
	print(f"  效率范围: {Config.MIN_EFFICIENCY*100:.1f}% - {Config.MAX_EFFICIENCY*100:.1f}%")
	print(f"  PPO学习率: {Config.PPO_CONFIG['learning_rate']}")
	print(f"  批大小: {Config.PPO_CONFIG['batch_size']}")
	print("="*60)
	
	# 开始训练
	try:
		reward_history = train_ppo_model(
			total_timesteps=36000,
			batch_size=4096
		)
		
		# 显示训练结果摘要
		if reward_history:
			final_reward = np.mean(reward_history[-100:])  # 最后100步平均奖励
			max_reward = np.max(reward_history)
			print(f"\n📈 训练结果摘要:")
			print(f"  最终平均奖励: {final_reward:.2f}")
			print(f"  最高奖励: {max_reward:.2f}")
		
		print("\n✅ 训练完成！")
		print("📁 检查以下目录获取结果:")
		print(f"  - 模型文件: {Config.MODEL_SAVE_PATH}")
		print(f"  - 可视化: E:/AI-based optimized design/Visualization/")
		print(f"  - TensorBoard: {Config.TENSORBOARD_LOG}")
		
	except Exception as e:
		print(f"\n❌ 训练过程中出现错误: {e}")
		import traceback
		traceback.print_exc()

if __name__ == '__main__':
	main()