"""
Buck变换器仿真系统
===================

本模块通过MATLAB Engine API自动化运行Buck变换器的Simulink仿真，
生成训练数据集用于后续的机器学习模型训练。

主要功能:
    - 启动并配置MATLAB环境
    - 加载并打开Simulink模型
    - 执行仿真脚本并收集数据
    - 保存仿真结果到CSV文件
"""

import matlab.engine
import time
import os
from typing import Optional


# ==================== 配置常量 ====================
class SimulationConfig:
    """仿真配置常量"""
    
    # 文件路径
    RESULT_FILE = 'E:/AI-based optimized design/Data/Input_Data/buck_data1.csv'
    MATLAB_SCRIPT = 'E:/AI-based optimized design/Code/matlab/BuckData.m'
    SIMULINK_DIR = 'E:/AI-based optimized design/Simulink'
    MODEL_NAME = 'Interleaved_parallel_buck'
    
    # MATLAB窗口配置
    MATLAB_WINDOW = {'left': 50, 'top': 50, 'width': 1000, 'height': 650}
    SIMULINK_WINDOW = {'left': 1100, 'top': 80, 'width': 900, 'height': 600}
    
    # 延迟配置（秒）
    MATLAB_STARTUP_DELAY = 10
    MODEL_LOAD_DELAY = 10
    MATLAB_SHUTDOWN_DELAY = 6


# ==================== MATLAB引擎管理 ====================
class MATLABEngineManager:
    """MATLAB引擎管理器，负责启动、配置和关闭MATLAB"""
    
    def __init__(self, config: SimulationConfig):
        """
        初始化MATLAB引擎管理器
        
        Args:
            config: 仿真配置对象
        """
        self.config = config
        self.engine: Optional[matlab.engine.MatlabEngine] = None
    
    def start_matlab(self) -> bool:
        """
        启动MATLAB引擎和桌面界面
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        print("正在启动MATLAB...")
        try:
            self.engine = matlab.engine.start_matlab()
            print("✓ MATLAB启动成功")
            
            # 启动桌面界面
            self._start_desktop()
            
            # 等待MATLAB完全加载
            print("正在加载MATLAB界面...")
            time.sleep(self.config.MATLAB_STARTUP_DELAY)
            print("✓ MATLAB界面加载成功")
            
            return True
            
        except Exception as e:
            print(f"✗ MATLAB启动失败: {e}")
            return False
    
    def _start_desktop(self) -> None:
        """启动MATLAB桌面界面并调整窗口大小"""
        try:
            self.engine.eval("desktop", nargout=0)
            print("✓ MATLAB桌面界面已启动")
            
            # 调整窗口大小和位置
            self._set_window_position()
            
        except Exception as e:
            print(f"提示: MATLAB桌面界面可能无法自动启动: {e}")
    
    def _set_window_position(self) -> None:
        """设置MATLAB桌面窗口位置和大小"""
        try:
            cmd = (
                "jDesktop = com.mathworks.mde.desk.MLDesktop.getInstance; "
                "jFrame = jDesktop.getMainFrame; "
                f"jFrame.setBounds({self.config.MATLAB_WINDOW['left']}, "
                f"{self.config.MATLAB_WINDOW['top']}, "
                f"{self.config.MATLAB_WINDOW['width']}, "
                f"{self.config.MATLAB_WINDOW['height']});"
            )
            self.engine.eval(cmd, nargout=0)
        except Exception as e:
            print(f"提示: 无法调整MATLAB桌面窗口大小: {e}")
    
    def quit(self) -> None:
        """关闭MATLAB引擎"""
        if self.engine is None:
            return
        
        print("正在关闭MATLAB...")
        time.sleep(self.config.MATLAB_SHUTDOWN_DELAY)
        
        try:
            self.engine.quit()
            print("✓ MATLAB已关闭")
        except Exception as e:
            print(f"✗ MATLAB关闭时出错: {e}")
        finally:
            self.engine = None
    
    def get_engine(self) -> Optional[matlab.engine.MatlabEngine]:
        """获取MATLAB引擎实例"""
        return self.engine


# ==================== Simulink模型管理 ====================
class SimulinkModelManager:
    """Simulink模型管理器，负责加载和配置模型"""
    
    def __init__(self, engine: matlab.engine.MatlabEngine, config: SimulationConfig):
        """
        初始化Simulink模型管理器
        
        Args:
            engine: MATLAB引擎实例
            config: 仿真配置对象
        """
        self.engine = engine
        self.config = config
    
    def validate_files(self) -> bool:
        """
        验证必要文件是否存在
        
        Returns:
            bool: 所有文件都存在返回True，否则返回False
        """
        # 检查MATLAB脚本
        if not os.path.exists(self.config.MATLAB_SCRIPT):
            print(f"✗ 找不到MATLAB脚本文件: {self.config.MATLAB_SCRIPT}")
            return False
        
        # 检查Simulink模型
        model_path = os.path.join(self.config.SIMULINK_DIR, f"{self.config.MODEL_NAME}.slx")
        if not os.path.exists(model_path):
            print(f"✗ 找不到Simulink模型文件: {model_path}")
            return False
        
        return True
    
    def load_model(self) -> bool:
        """
        加载Simulink模型并打开模型界面
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        print("正在加载Simulink模型...")
        time.sleep(self.config.MODEL_LOAD_DELAY)
        
        try:
            # 切换到Simulink目录
            self.engine.eval(f"cd('{self.config.SIMULINK_DIR}')", nargout=0)
            
            # 加载模型
            self.engine.eval(f"load_system('{self.config.MODEL_NAME}')", nargout=0)
            
            # 打开模型界面
            self.engine.eval(f"open_system('{self.config.MODEL_NAME}')", nargout=0)
            
            # 调整窗口位置
            self._set_model_window_position()
            
            # 设置显示参数
            self._configure_display_parameters()
            
            print("✓ Simulink模型加载成功")
            return True
            
        except Exception as e:
            print(f"✗ Simulink模型加载失败: {e}")
            return False
    
    def _set_model_window_position(self) -> None:
        """设置Simulink模型窗口位置和大小"""
        try:
            cfg = self.config.SIMULINK_WINDOW
            left, top = cfg['left'], cfg['top']
            right = left + cfg['width']
            bottom = top + cfg['height']
            
            cmd = f"set_param('{self.config.MODEL_NAME}', 'Location', [{left} {top} {right} {bottom}])"
            self.engine.eval(cmd, nargout=0)
            
        except Exception as e:
            print(f"提示: 无法调整Simulink窗口位置: {e}")
    
    def _configure_display_parameters(self) -> None:
        """配置模型显示参数，使仿真过程更清晰"""
        try:
            self.engine.eval(
                f"set_param('{self.config.MODEL_NAME}', 'ShowPortDataTypes', 'on')",
                nargout=0
            )
            self.engine.eval(
                f"set_param('{self.config.MODEL_NAME}', 'ShowLineDimensions', 'on')",
                nargout=0
            )
        except Exception as e:
            print(f"提示: 无法设置显示参数: {e}")


# ==================== 仿真执行器 ====================
class SimulationExecutor:
    """仿真执行器，负责运行仿真脚本并收集结果"""
    
    def __init__(self, engine: matlab.engine.MatlabEngine, config: SimulationConfig):
        """
        初始化仿真执行器
        
        Args:
            engine: MATLAB引擎实例
            config: 仿真配置对象
        """
        self.engine = engine
        self.config = config
    
    def run_simulation(self) -> bool:
        """
        执行仿真并保存结果
        
        Returns:
            bool: 仿真成功返回True，失败返回False
        """
        print("\n" + "=" * 60)
        print("开始运行仿真...")
        print("=" * 60)
        
        try:
            start_time = time.time()
            print("正在执行BuckData.m脚本...")
            
            # 运行MATLAB脚本
            self.engine.eval(f"run('{self.config.MATLAB_SCRIPT}')", nargout=0)
            
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"\n✓ 仿真完成！总耗时: {elapsed_time:.2f} 秒")
            
            # 显示结果文件信息
            self._display_result_info()
            
            return True
            
        except Exception as e:
            print(f"✗ 仿真运行失败: {e}")
            return False
    
    def _display_result_info(self) -> None:
        """显示仿真结果文件信息"""
        if os.path.exists(self.config.RESULT_FILE):
            file_size = os.path.getsize(self.config.RESULT_FILE) / 1024  # KB
            print(f"✓ 结果已保存到: {self.config.RESULT_FILE}")
            print(f"  文件大小: {file_size:.2f} KB")
        else:
            print("⚠ 警告: 未找到结果文件")


# ==================== 主程序 ====================
def print_banner() -> None:
    """打印程序横幅"""
    print("=" * 60)
    print("Buck转换器仿真系统")
    print("=" * 60)


def print_completion_info() -> None:
    """打印完成信息"""
    print("\n" + "=" * 60)
    print("数据集获取完成! MATLAB界面将保持打开状态。")
    print("您可以:")
    print("1. 查看Simulink模型")
    print("2. 分析仿真结果")
    print("3. 查看生成的CSV数据文件")
    print("4. 在MATLAB工作区中查看变量")
    print("=" * 60)


def wait_for_user_input() -> None:
    """等待用户输入以保持MATLAB界面打开"""
    try:
        input("按回车键关闭MATLAB...")
    except KeyboardInterrupt:
        print("\n检测到中断信号...")


def main() -> None:
    """
    主函数：协调整个仿真流程
    
    流程:
        1. 启动MATLAB引擎
        2. 验证必要文件
        3. 加载Simulink模型
        4. 执行仿真脚本
        5. 保存结果
        6. 等待用户确认后关闭
    """
    print_banner()
    
    config = SimulationConfig()
    matlab_manager = MATLABEngineManager(config)
    
    # 启动MATLAB
    if not matlab_manager.start_matlab():
        return
    
    engine = matlab_manager.get_engine()
    
    try:
        # 验证文件
        model_manager = SimulinkModelManager(engine, config)
        if not model_manager.validate_files():
            return
        
        # 加载模型
        if not model_manager.load_model():
            return
        
        # 运行仿真
        executor = SimulationExecutor(engine, config)
        if not executor.run_simulation():
            return
        
        # 显示完成信息
        print_completion_info()
        
        # 等待用户输入
        wait_for_user_input()
        
    finally:
        # 确保MATLAB引擎被正确关闭
        matlab_manager.quit()


# ==================== 入口点 ====================
if __name__ == "__main__":
    main()
