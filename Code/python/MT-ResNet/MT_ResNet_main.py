"""
MT-ResNet: Multi-Task Residual Network for Buck Converter Performance Prediction
================================================================================

本模块实现了基于残差网络的多任务学习模型，用于预测Buck变换器的性能指标。
模型同时预测两个输出：电压纹波系数和效率。

主要功能:
    - 数据加载和预处理（标准化）
    - 构建多任务残差网络
    - 模型训练与评估
    - 可视化预测结果
    - 保存训练好的模型

架构特点:
    - 5层残差块，逐层降维（512→384→256→128→64）
    - BatchNormalization + LeakyReLU + Dropout
    - He初始化适配ReLU族激活函数
    - 早停机制防止过拟合
    - 分段学习率衰减
"""

import os
import sys
from typing import Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.models import Model
from keras.layers import Input, Dense, BatchNormalization, LeakyReLU, Dropout, Add
from keras.optimizers import Adam
from keras.initializers import HeNormal
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 抑制TensorFlow日志噪声
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 设置随机种子以保证可复现性
np.random.seed(42)
tf.random.set_seed(42)


# ==================== 配置管理 ====================
@dataclass
class PathConfig:
    """文件路径配置"""
    data_csv: str = 'E:/AI-based optimized design/Data/Input_Data/buck_data1.csv'
    x_stats_csv: str = 'E:/AI-based optimized design/Data/Input_Data/x_scaled_data.csv'
    y_stats_csv: str = 'E:/AI-based optimized design/Data/Input_Data/y_scaled_data.csv'
    plot_line: str = 'E:/AI-based optimized design/Visualization/prediction_comparison.png'
    plot_scatter: str = 'E:/AI-based optimized design/Visualization/scatter_plots.png'
    model_out: str = 'E:/AI-based optimized design/Trained_model/trainedNet.keras'


@dataclass
class ModelConfig:
    """模型超参数配置"""
    # 网络结构配置
    units: List[int] = None  # 各残差块的隐藏单元数
    dropout_rates: List[float] = None  # 各残差块的dropout比例
    
    # 训练配置
    epochs: int = 800  # 最大训练轮数
    batch_size: int = 128  # 批次大小
    learning_rate: float = 0.0015  # 初始学习率
    early_stop_patience: int = 25  # 早停耐心值
    validation_split: float = 0.2  # 验证集比例
    validation_freq: int = 50  # 验证频率（每N个epoch验证一次）
    
    # 学习率调度配置
    lr_initial: float = 0.001  # 学习率调度初始值
    lr_drop_factor: float = 0.2  # 学习率衰减因子
    lr_drop_epochs: int = 250  # 每N个epoch衰减一次
    
    def __post_init__(self):
        """初始化默认配置"""
        if self.units is None:
            self.units = [512, 384, 256, 128, 64]
        if self.dropout_rates is None:
            self.dropout_rates = [0.25, 0.25, 0.2, 0.2, 0.15]
        
        # 验证配置合法性
        if len(self.units) != len(self.dropout_rates):
            raise ValueError("units和dropout_rates长度必须相同")


# ==================== 数据管理器 ====================
class DataManager:
    """数据加载、预处理和划分管理器"""
    
    def __init__(self, path_config: PathConfig, model_config: ModelConfig):
        """
        初始化数据管理器
        
        Args:
            path_config: 路径配置对象
            model_config: 模型配置对象
        """
        self.path_config = path_config
        self.model_config = model_config
        self.scaler_x: Optional[StandardScaler] = None
        self.scaler_y: Optional[StandardScaler] = None
    
    def check_dataset_exists(self) -> bool:
        """
        检查数据集文件是否存在，并显示文件信息
        
        Returns:
            bool: 文件存在返回True，否则返回False
        """
        if not os.path.exists(self.path_config.data_csv):
            return False
        
        print("\n" + "=" * 60)
        print("检测到数据集文件已存在")
        print("=" * 60)
        
        # 显示文件信息
        file_stat = os.stat(self.path_config.data_csv)
        file_size = file_stat.st_size / 1024  # KB
        mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        
        print(f"文件路径: {self.path_config.data_csv}")
        print(f"文件大小: {file_size:.2f} KB")
        print(f"修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示数据预览
        self._display_data_preview()
        
        return True
    
    def _display_data_preview(self) -> None:
        """显示数据文件预览"""
        try:
            df = pd.read_csv(self.path_config.data_csv)
            print(f"数据行数: {len(df)}")
            print(f"数据列数: {len(df.columns)}")
            print(f"列名: {', '.join(df.columns.tolist())}")
            
            print("\n数据预览(前3行):")
            print(df.head(3).to_string(index=False))
            
        except Exception as e:
            print(f"无法读取文件内容: {e}")
    
    def prompt_regenerate_data(self) -> bool:
        """
        询问用户是否重新生成数据
        
        Returns:
            bool: 用户选择重新生成返回True，否则返回False
        """
        while True:
            user_input = input("\n数据集已存在,是否重新生成数据？(y/n): ").strip().lower()
            if user_input in ['y', 'yes']:
                print("将重新生成数据并覆盖现有数据集。")
                return True
            elif user_input in ['n', 'no']:
                print("跳过数据生成，使用现有数据集。")
                print("\n" + "=" * 60)
                return False
            else:
                print("请输入 'y' 或 'n'")
    
    def generate_data(self) -> None:
        """调用Buck_Data模块生成数据集"""
        try:
            from Buck_Data import main as buck_main
            buck_main()
        except ImportError as e:
            print(f"错误: 无法导入Buck_Data模块: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 数据生成失败: {e}")
            sys.exit(1)
    
    def load_and_preprocess(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        加载数据、标准化并划分训练/测试集
        
        Returns:
            tuple: (x_train, x_test, y_train, y_test)
            
        Raises:
            FileNotFoundError: 数据文件不存在
        """
        if not os.path.exists(self.path_config.data_csv):
            raise FileNotFoundError(f'数据文件未找到: {self.path_config.data_csv}')
        
        # 加载数据
        data = pd.read_csv(self.path_config.data_csv)
        
        # 提取输入和输出
        input_cols = ['f(Hz)', 'L(H)', 'C(F)', 'Ron', 'RL', 'RC']
        output_cols = ['Vo_Ripple_factor', 'Efficiency']
        
        x = data[input_cols].values
        y = data[output_cols].values
        
        # 标准化输入数据
        self.scaler_x = StandardScaler()
        x_scaled = self.scaler_x.fit_transform(x)
        
        # 保存输入标准化统计量
        self._save_scaler_stats(
            self.scaler_x, 
            self.path_config.x_stats_csv, 
            ['x_mu', 'x_sigma']
        )
        
        # 标准化输出数据
        self.scaler_y = StandardScaler()
        y_scaled = self.scaler_y.fit_transform(y)
        
        # 保存输出标准化统计量
        self._save_scaler_stats(
            self.scaler_y, 
            self.path_config.y_stats_csv, 
            ['y_mu', 'y_sigma']
        )
        
        # 划分训练/测试集
        x_train, x_test, y_train, y_test = train_test_split(
            x_scaled, 
            y_scaled, 
            test_size=self.model_config.validation_split, 
            random_state=42
        )
        
        return x_train, x_test, y_train, y_test
    
    def _save_scaler_stats(
        self, 
        scaler: StandardScaler, 
        file_path: str, 
        col_names: List[str]
    ) -> None:
        """
        保存StandardScaler的统计量到CSV文件
        
        Args:
            scaler: StandardScaler对象
            file_path: 保存路径
            col_names: 列名列表
        """
        df = pd.DataFrame({
            col_names[0]: scaler.mean_,
            col_names[1]: scaler.scale_
        })
        df.to_csv(file_path, index=False)
    
    def get_y_scaler(self) -> Optional[StandardScaler]:
        """获取输出数据的标准化器"""
        return self.scaler_y


# ==================== 模型构建器 ====================
class MTResNetBuilder:
    """多任务残差网络构建器"""
    
    def __init__(self, model_config: ModelConfig):
        """
        初始化模型构建器
        
        Args:
            model_config: 模型配置对象
        """
        self.config = model_config
    
    def build(self) -> Model:
        """
        构建MT-ResNet模型
        
        Returns:
            Model: Keras模型实例
        """
        # 输入层（6个特征: f, L, C, Ron, RL, RC）
        inputs = Input(shape=(6,), name='input')
        
        # 堆叠残差块
        x = inputs
        for i, (units, dropout) in enumerate(
            zip(self.config.units, self.config.dropout_rates), 
            start=1
        ):
            x = self._residual_block(
                x, 
                units=units, 
                name=f'block{i}', 
                dropout_rate=dropout
            )
        
        # 输出层（2个输出: 纹波系数, 效率）
        outputs = Dense(2, name='output')(x)
        
        # 构建模型
        model = Model(inputs=inputs, outputs=outputs, name='MT_ResNet')
        
        return model
    
    def _residual_block(
        self, 
        inputs: tf.Tensor, 
        units: int, 
        name: str, 
        dropout_rate: float
    ) -> tf.Tensor:
        """
        构建残差块
        
        残差块结构:
            主分支: Dense → BN → LeakyReLU → Dropout → Dense → BN
            旁路分支: Dense（维度匹配）
            输出: Add(主分支, 旁路分支) → ReLU
        
        Args:
            inputs: 输入张量
            units: 隐藏单元数
            name: 层名称前缀
            dropout_rate: Dropout比例
            
        Returns:
            tf.Tensor: 残差块输出张量
        """
        # 主分支
        x = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_fc1')(inputs)
        x = BatchNormalization(name=f'{name}_bn1')(x)
        x = LeakyReLU(negative_slope=0.1, name=f'{name}_lrelu1')(x)
        x = Dropout(dropout_rate, name=f'{name}_drop1')(x)
        x = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_fc2')(x)
        x = BatchNormalization(name=f'{name}_bn2')(x)
        
        # 旁路分支（维度匹配）
        skip = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_skip')(inputs)
        
        # 残差连接
        out = Add(name=f'{name}_add')([x, skip])
        out = tf.keras.layers.ReLU(name=f'{name}_out')(out)
        
        return out


# ==================== 训练器 ====================
class ModelTrainer:
    """模型训练器"""
    
    def __init__(self, model_config: ModelConfig):
        """
        初始化训练器
        
        Args:
            model_config: 模型配置对象
        """
        self.config = model_config
    
    def train(
        self, 
        model: Model, 
        x_train: np.ndarray, 
        y_train: np.ndarray,
        x_test: np.ndarray, 
        y_test: np.ndarray
    ) -> Model:
        """
        训练模型
        
        Args:
            model: Keras模型
            x_train: 训练集输入
            y_train: 训练集输出
            x_test: 测试集输入
            y_test: 测试集输出
            
        Returns:
            Model: 训练好的模型
        """
        print('\n开始训练模型...')
        print("=" * 60)
        
        # 编译模型
        model.compile(
            optimizer=Adam(learning_rate=self.config.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        # 训练回调
        callbacks = self._create_callbacks()
        
        # 训练
        history = model.fit(
            x_train, y_train,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            validation_data=(x_test, y_test),
            validation_freq=self.config.validation_freq,
            callbacks=callbacks,
            verbose=1
        )
        
        print("\n✓ 训练完成")
        return model
    
    def _create_callbacks(self) -> List[tf.keras.callbacks.Callback]:
        """
        创建训练回调
        
        Returns:
            list: 回调列表
        """
        callbacks = [
            # 早停回调
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config.early_stop_patience,
                restore_best_weights=True,
                min_delta=1e-6,
                verbose=1
            ),
            # 学习率调度回调
            tf.keras.callbacks.LearningRateScheduler(
                self._lr_schedule,
                verbose=1
            )
        ]
        
        return callbacks
    
    def _lr_schedule(self, epoch: int) -> float:
        """
        学习率调度函数（分段衰减）
        
        Args:
            epoch: 当前epoch数
            
        Returns:
            float: 当前学习率
        """
        lr = self.config.lr_initial * (
            self.config.lr_drop_factor ** (epoch // self.config.lr_drop_epochs)
        )
        return lr


# ==================== 评估器 ====================
class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self, scaler_y: StandardScaler):
        """
        初始化评估器
        
        Args:
            scaler_y: 输出数据的标准化器
        """
        self.scaler_y = scaler_y
    
    def evaluate(
        self, 
        model: Model, 
        x_test: np.ndarray, 
        y_test: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        评估模型并打印指标
        
        Args:
            model: 训练好的模型
            x_test: 测试集输入
            y_test: 测试集输出（标准化后）
            
        Returns:
            tuple: (真实值, 预测值) - 都已反标准化
        """
        print("\n开始评估模型...")
        print("=" * 60)
        
        # 预测
        y_pred = model.predict(x_test, verbose=0)
        
        # 反标准化
        y_test_true = self.scaler_y.inverse_transform(y_test)
        y_pred_true = self.scaler_y.inverse_transform(y_pred)
        
        # 计算并打印指标
        self._print_metrics(y_test_true, y_pred_true)
        
        return y_test_true, y_pred_true
    
    def _print_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> None:
        """
        计算并打印评估指标
        
        Args:
            y_true: 真实值
            y_pred: 预测值
        """
        # 纹波系数指标
        ripple_mse = mean_squared_error(y_true[:, 0], y_pred[:, 0])
        ripple_mae = mean_absolute_error(y_true[:, 0], y_pred[:, 0])
        ripple_r2 = r2_score(y_true[:, 0], y_pred[:, 0])
        
        # 效率指标
        eff_mse = mean_squared_error(y_true[:, 1], y_pred[:, 1])
        eff_mae = mean_absolute_error(y_true[:, 1], y_pred[:, 1])
        eff_r2 = r2_score(y_true[:, 1], y_pred[:, 1])
        
        print('\n纹波系数评估:')
        print(f'  MSE: {ripple_mse:.8f}')
        print(f'  MAE: {ripple_mae:.8f}')
        print(f'  R²:  {ripple_r2:.6f}')
        
        print('\n效率评估:')
        print(f'  MSE: {eff_mse:.8f}')
        print(f'  MAE: {eff_mae:.8f}')
        print(f'  R²:  {eff_r2:.6f}')
        print('=' * 60)


# ==================== 可视化器 ====================
class ResultVisualizer:
    """结果可视化器"""
    
    def __init__(self, path_config: PathConfig):
        """
        初始化可视化器
        
        Args:
            path_config: 路径配置对象
        """
        self.path_config = path_config
    
    def plot_comparison(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> None:
        """
        绘制预测值与真实值对比折线图
        
        Args:
            y_true: 真实值 (N, 2)
            y_pred: 预测值 (N, 2)
        """
        print("\n生成对比图...")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # 纹波系数对比
        ax1.plot(y_true[:, 0], '-*r', linewidth=1, label='Actual Ripple', markersize=3)
        ax1.plot(y_pred[:, 0], '-sb', linewidth=1, label='Predicted Ripple', markersize=3)
        ax1.set_title('Voltage Ripple Factor Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Ripple Factor', fontsize=12)
        ax1.legend(fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(labelsize=10)
        
        # 效率对比
        ax2.plot(y_true[:, 1], '-*g', linewidth=1, label='Actual Efficiency', markersize=3)
        ax2.plot(y_pred[:, 1], '-om', linewidth=1, label='Predicted Efficiency', markersize=3)
        ax2.set_title('Efficiency Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Sample Index', fontsize=12)
        ax2.set_ylabel('Efficiency', fontsize=12)
        ax2.legend(fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(labelsize=10)
        
        plt.tight_layout()
        plt.savefig(self.path_config.plot_line, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✓ 对比图已保存: {self.path_config.plot_line}")
    
    def plot_scatter(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> None:
        """
        绘制预测精度散点图
        
        Args:
            y_true: 真实值 (N, 2)
            y_pred: 预测值 (N, 2)
        """
        print("\n生成散点图...")
        
        # 计算R²
        ripple_r2 = r2_score(y_true[:, 0], y_pred[:, 0])
        eff_r2 = r2_score(y_true[:, 1], y_pred[:, 1])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 纹波系数散点图
        ax1.scatter(y_true[:, 0], y_pred[:, 0], alpha=0.6, s=20)
        min_val, max_val = y_true[:, 0].min(), y_true[:, 0].max()
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        ax1.set_title('Ripple Factor: Actual vs Predicted', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Actual Values', fontsize=12)
        ax1.set_ylabel('Predicted Values', fontsize=12)
        ax1.grid(True, linestyle='--', alpha=0.3)
        ax1.text(
            0.05, 0.95, f'R² = {ripple_r2:.4f}',
            transform=ax1.transAxes,
            fontsize=12, va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        ax1.legend()
        
        # 效率散点图
        ax2.scatter(y_true[:, 1], y_pred[:, 1], alpha=0.6, s=20, color='green')
        min_val, max_val = y_true[:, 1].min(), y_true[:, 1].max()
        ax2.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
        ax2.set_title('Efficiency: Actual vs Predicted', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Actual Values', fontsize=12)
        ax2.set_ylabel('Predicted Values', fontsize=12)
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.text(
            0.05, 0.95, f'R² = {eff_r2:.4f}',
            transform=ax2.transAxes,
            fontsize=12, va='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        ax2.legend()
        
        plt.tight_layout()
        plt.savefig(self.path_config.plot_scatter, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"✓ 散点图已保存: {self.path_config.plot_scatter}")


# ==================== 主程序流程 ====================
def print_banner() -> None:
    """打印程序横幅"""
    print("=" * 60)
    print("Buck性能预测模型 - MT-ResNet")
    print("=" * 60)


def train_evaluate_visualize() -> None:
    """
    主训练流程：数据加载 → 训练 → 评估 → 可视化 → 保存
    """
    # 初始化配置
    path_config = PathConfig()
    model_config = ModelConfig()
    
    # 数据管理
    data_manager = DataManager(path_config, model_config)
    
    # 检查数据集
    if data_manager.check_dataset_exists():
        if data_manager.prompt_regenerate_data():
            data_manager.generate_data()
    else:
        print("数据集CSV文件不存在,开始生成数据集...")
        data_manager.generate_data()
    
    # 加载和预处理数据
    print("\n加载数据...")
    x_train, x_test, y_train, y_test = data_manager.load_and_preprocess()
    print(f"✓ 训练集大小: {x_train.shape[0]} 样本")
    print(f"✓ 测试集大小: {x_test.shape[0]} 样本")
    
    # 构建模型
    print("\n构建模型...")
    builder = MTResNetBuilder(model_config)
    model = builder.build()
    model.summary()
    
    # 训练模型
    trainer = ModelTrainer(model_config)
    model = trainer.train(model, x_train, y_train, x_test, y_test)
    
    # 评估模型
    evaluator = ModelEvaluator(data_manager.get_y_scaler())
    y_true, y_pred = evaluator.evaluate(model, x_test, y_test)
    
    # 可视化结果
    visualizer = ResultVisualizer(path_config)
    visualizer.plot_comparison(y_true, y_pred)
    visualizer.plot_scatter(y_true, y_pred)
    
    # 保存模型
    print(f"\n保存模型到: {path_config.model_out}")
    model.save(path_config.model_out)
    print("✓ 模型已保存")
    
    print("\n" + "=" * 60)
    print("所有任务完成！")
    print("=" * 60)


# ==================== 入口点 ====================
if __name__ == '__main__':
    print_banner()
    
    try:
        train_evaluate_visualize()
    except KeyboardInterrupt:
        print("\n\n⚠ 训练被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
