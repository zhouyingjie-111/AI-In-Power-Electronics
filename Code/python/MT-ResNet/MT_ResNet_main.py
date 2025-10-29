import numpy as np
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 降低 TensorFlow 日志噪声
import tensorflow as tf
from keras.models import Model
from keras.layers import Input, Dense, BatchNormalization, LeakyReLU, Dropout, Add
from keras.optimizers import Adam
from keras.initializers import HeNormal
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from datetime import datetime

# 复现性设置
np.random.seed(42)
tf.random.set_seed(42)

# 文件路径
DATA_CSV = 'E:/AI-based optimized design/Data/Input_Data/buck_data1.csv'
X_STATS_CSV = 'E:/AI-based optimized design/Data/Input_Data/x_scaled_data.csv'
Y_STATS_CSV = 'E:/AI-based optimized design/Data/Input_Data/y_scaled_data.csv'
PLOT_LINE = 'E:/AI-based optimized design/Picture/prediction_comparison.png'
PLOT_SCATTER = 'E:/AI-based optimized design/Picture/scatter_plots.png'
MODEL_OUT = 'E:/AI-based optimized design/Trained_model/trainedNet.keras'

# 模型配置
UNITS_CFG = [512, 384, 256, 128, 64]       # 各残差块的隐藏单元数配置
DROPOUT_CFG = [0.25, 0.25, 0.2, 0.2, 0.15] # 各残差块的 dropout 比例
EPOCHS = 800                               # 最大学习轮数
BATCH_SIZE = 128                           # 每个迭代的批大小
LEARNING_RATE = 0.0015                     # Adam 优化器的初始学习率：值越大收敛越快但可能不稳定
EARLY_STOP_PATIENCE = 25                   # 早停耐心值：验证集无改进达到该轮数后停止训练并回滚最佳权重

print("=" * 60)
print("Buck性能预测模型")
print("=" * 60)

# 检查CSV文件是否存在
if os.path.exists(DATA_CSV):
    print("\n" + "=" * 60)
    print("检测到数据集文件已存在")
    print("=" * 60)
        
    # 获取文件信息
    file_stat = os.stat(DATA_CSV)
    file_size = file_stat.st_size / 1024  # KB
    mod_time = datetime.fromtimestamp(file_stat.st_mtime)
        
    print(f"文件路径: {DATA_CSV}")
    print(f"文件大小: {file_size:.2f} KB")
    print(f"修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    # 尝试读取并显示文件基本信息
    try:
        df = pd.read_csv(DATA_CSV)
        print(f"数据行数: {len(df)}")
        print(f"数据列数: {len(df.columns)}")
        print(f"列名: {', '.join(df.columns.tolist())}")
            
        # 显示前几行数据预览
        print("\n数据预览(前3行):")
        print(df.head(3).to_string(index=False))
            
    except Exception as e:
        print(f"无法读取文件内容: {e}")
        
    # 询问用户是否重新生成
    while True:
        user_input = input("\n数据集已存在,是否重新生成数据？(y/n): ").strip().lower()
        if user_input in ['y', 'yes', 'n', 'no']:
            break
        print("请输入 'y' 或 'n'")
        
    if user_input in ['n', 'no']:
        print("跳过数据生成，使用现有数据集。")
        print("\n" + "=" * 60)
    else:
        print("将重新生成数据并覆盖现有数据集。")
        from Buck_Data import main as buck_main
        buck_main()
else:
    print("数据集CSV文件不存在,开始生成数据集...")
    from Buck_Data import main as buck_main
    buck_main()


"""
读取数据, 标准化, 划分训练/测试集并保存

返回: (x_train, x_test, y_train, y_test, scaler_y)
说明: 仅返回用于反标准化的 y 缩放器, 避免不必要对象暴露
"""
def load_and_scale_data(csv_path: str):

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'数据文件未找到: {csv_path}')

    data = pd.read_csv(csv_path)

    # 输入/输出数据
    x = data[['f(Hz)', 'L(H)', 'C(F)', 'Ron', 'RL', 'RC']].values
    y = data[['Vo_Ripple_factor', 'Efficiency']].values

    scaler_x = StandardScaler()
    x_scaled = scaler_x.fit_transform(x)

    # 保存输入标准化统计量
    pd.DataFrame({'x_mu': scaler_x.mean_, 'x_sigma': scaler_x.scale_}).to_csv(X_STATS_CSV, index=False)

    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y)

    # 保存输出标准化统计量
    pd.DataFrame({'y_mu': scaler_y.mean_, 'y_sigma': scaler_y.scale_}).to_csv(Y_STATS_CSV, index=False)

    x_train, x_test, y_train, y_test = train_test_split(
        x_scaled, y_scaled, test_size=0.2, random_state=42
    )
    return x_train, x_test, y_train, y_test, scaler_y

"""
通用残差块: 两层全连接 + BN/激活/Dropout, 并与输入做残差相加。

参数:
    inputs: 上一层张量作为该残差块的输入
    units: 该残差块主分支所使用的隐藏单元数
    name: 残差块的命名前缀, 用于区分不同块的层名
    dropout_rate: 该残差块使用的 dropout 比例
"""
def _residual_block(inputs, units: int, name: str, dropout_rate: float):

    x = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_fc1')(inputs)  # 主分支第1个全连接, He初始化适合ReLU族
    x = BatchNormalization(name=f'{name}_bn1')(x)                                # BN稳定分布, 加速收敛
    x = LeakyReLU(negative_slope=0.1, name=f'{name}_lrelu1')(x)                  # 使用LeakyReLU缓解ReLU死亡问题
    x = Dropout(dropout_rate, name=f'{name}_drop1')(x)                           # 随机丢弃以减少过拟合
    x = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_fc2')(x)       # 主分支第2个全连接, 维度与units一致
    x = BatchNormalization(name=f'{name}_bn2')(x)                                # 再做一次BN保持数值稳定
    skip = Dense(units, kernel_initializer=HeNormal(), name=f'{name}_skip')(inputs)  # 旁路分支将输入映射到同维度以匹配主分支
    out = Add(name=f'{name}_add')([x, skip])                                     # 主分支与旁路分支逐元素相加形成残差连接
    out = tf.keras.layers.ReLU(name=f'{name}_out')(out)                          # 残差相加后再做激活, 提升表达与稳定性
    return out  # 返回该残差块的输出

"""
构建多任务全连接残差网络(2个任务: 纹波系数与效率)

返回: 多任务MT-ResNet模型实例
"""
def build_mt_resnet():

    inputs = Input(shape=(6,), name='input')  # 输入向量维度为6: f/L/C/Ron/RL/RC
    x = _residual_block(inputs, units=UNITS_CFG[0], name='block1', dropout_rate=DROPOUT_CFG[0])  # 残差块1
    y = _residual_block(x, units=UNITS_CFG[1], name='block2', dropout_rate=DROPOUT_CFG[1])       # 残差块2
    z = _residual_block(y, units=UNITS_CFG[2], name='block3', dropout_rate=DROPOUT_CFG[2])       # 残差块3
    a = _residual_block(z, units=UNITS_CFG[3], name='block4', dropout_rate=DROPOUT_CFG[3])       # 残差块4
    b = _residual_block(a, units=UNITS_CFG[4], name='block5', dropout_rate=DROPOUT_CFG[4])       # 残差块5
    outputs = Dense(2, name='output')(b)
    return Model(inputs=inputs, outputs=outputs, name='MT_ResNet')  # 构建Keras模型实例

"""
分段衰减学习率
"""
def lr_schedule(epoch: int) -> float:

    initial_lr, drop_factor, drop_epochs = 0.001, 0.2, 250
    return initial_lr * (drop_factor ** (epoch // drop_epochs))

"""
训练 -> 评估 -> 可视化 -> 保存模型。
"""
def train_evaluate_plot():
    print('开始训练模型')
    x_train, x_test, y_train, y_test, scaler_y = load_and_scale_data(DATA_CSV)

    model = build_mt_resnet()
    # 模型配置
    model.compile(optimizer=Adam(learning_rate=LEARNING_RATE), loss='mse', metrics=['mae'])

    # 训练回调: 早停+学习率调度
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=EARLY_STOP_PATIENCE, restore_best_weights=True, min_delta=1e-6),
        tf.keras.callbacks.LearningRateScheduler(lr_schedule),
    ]

    model.fit(
        x_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(x_test, y_test),
        validation_freq=50,
        callbacks=callbacks,
        verbose=1,
    )

    # 反标准化并评估
    y_pred = model.predict(x_test)
    y_test_true = scaler_y.inverse_transform(y_test)
    y_pred_true = scaler_y.inverse_transform(y_pred)

    ripple_mse = mean_squared_error(y_test_true[:, 0], y_pred_true[:, 0])
    ripple_mae = mean_absolute_error(y_test_true[:, 0], y_pred_true[:, 0])
    ripple_r2 = r2_score(y_test_true[:, 0], y_pred_true[:, 0])

    eff_mse = mean_squared_error(y_test_true[:, 1], y_pred_true[:, 1])
    eff_mae = mean_absolute_error(y_test_true[:, 1], y_pred_true[:, 1])
    eff_r2 = r2_score(y_test_true[:, 1], y_pred_true[:, 1])

    print('\n' + '=' * 50)
    print('纹波系数评估:')
    print(f'MSE: {ripple_mse:.8f}, MAE: {ripple_mae:.8f}, R²: {ripple_r2:.6f}')
    print('\n效率评估:')
    print(f'MSE: {eff_mse:.8f}, MAE: {eff_mae:.8f}, R²: {eff_r2:.6f}')
    print('=' * 50)

    # 折线对比图
    plt.figure(figsize=(14, 10))
    plt.subplot(2, 1, 1)
    plt.plot(y_test_true[:, 0], '-*r', linewidth=1, label='Actual Ripple')
    plt.plot(y_pred_true[:, 0], '-sb', linewidth=1, label='Predicted Ripple')
    plt.title('Voltage Ripple Factor Comparison', fontsize=14)
    plt.ylabel('Ripple Factor', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)

    plt.subplot(2, 1, 2)
    plt.plot(y_test_true[:, 1], '-*g', linewidth=1, label='Actual Efficiency')
    plt.plot(y_pred_true[:, 1], '-om', linewidth=1, label='Predicted Efficiency')
    plt.title('Efficiency Comparison', fontsize=14)
    plt.ylabel('Efficiency', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(PLOT_LINE)
    plt.show()

    # 散点精度图
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    plt.scatter(y_test_true[:, 0], y_pred_true[:, 0], alpha=0.6)
    plt.plot([min(y_test_true[:, 0]), max(y_test_true[:, 0])],
             [min(y_test_true[:, 0]), max(y_test_true[:, 0])], 'r--', linewidth=2)
    plt.title('Ripple Factor: Actual vs Predicted', fontsize=14)
    plt.xlabel('Actual Values', fontsize=12)
    plt.ylabel('Predicted Values', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.text(0.05, 0.95, f'R² = {ripple_r2:.4f}', transform=plt.gca().transAxes,
             fontsize=12, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.subplot(1, 2, 2)
    plt.scatter(y_test_true[:, 1], y_pred_true[:, 1], alpha=0.6, color='green')
    plt.plot([min(y_test_true[:, 1]), max(y_test_true[:, 1])],
             [min(y_test_true[:, 1]), max(y_test_true[:, 1])], 'r--', linewidth=2)
    plt.title('Efficiency: Actual vs Predicted', fontsize=14)
    plt.xlabel('Actual Values', fontsize=12)
    plt.ylabel('Predicted Values', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.text(0.05, 0.95, f'R² = {eff_r2:.4f}', transform=plt.gca().transAxes,
             fontsize=12, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    plt.tight_layout()
    plt.savefig(PLOT_SCATTER)
    plt.show()

    # 保存模型
    model.save(MODEL_OUT)
    print(f'\n模型已保存至: {MODEL_OUT}')

# 执行入口
if __name__ == '__main__':
    # 单文件执行入口
    train_evaluate_plot()