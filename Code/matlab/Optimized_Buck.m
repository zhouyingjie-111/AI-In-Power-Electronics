% 基于最优设计参数进行单次仿真验证
%% 工作区预处理
clc;
clear;
close;

%% 关闭警告信息
warning('off');    

%% 检查并读取最优设计参数
optimal_design_path = 'E:\AI-based optimized design\Visualization\optimal_design.csv';

if exist(optimal_design_path, 'file')
    fprintf('正在读取最优设计参数: %s\n', optimal_design_path);
    
    % 读取CSV文件
    try
        optimal_data = readtable(optimal_design_path);
        fprintf('成功读取最优设计参数\n');
        fprintf('数据行数: %d\n', height(optimal_data));
        fprintf('数据列数: %d\n', width(optimal_data));
        fprintf('列名: %s\n', strjoin(optimal_data.Properties.VariableNames, ', '));
        
        % 显示数据预览
        fprintf('\n最优设计参数预览:\n');
        disp(optimal_data);
        
    catch ME
        fprintf('读取最优设计参数失败: %s\n', ME.message);
        return;
    end
else
    fprintf('找不到最优设计参数文件: %s\n', optimal_design_path);
    fprintf('请先运行PPO优化程序生成最优设计参数\n');
    return;
end

%% 数据初始化
Vo = [];
Pin = [];
Po = [];
Eff = [];
Psw1 = [];
Psw2 = [];
Prl = [];
Prc = [];
f_record = [];
L_record = [];
C_record = [];
Ron_record = [];
RL_record = [];
RC_record = [];
Vo_Ripple_record = [];
Vo_Ripple_factor_record = [];

% 设置仿真次数（单次仿真）
sum = 1;    % 单次仿真
n = 1;      % 每批仿真次数
num_batches = 1; % 单批次

% 设置随机种子
rng(0); 

%% 读取模型
% 模型路径
model_path = 'E:\AI-based optimized design\Simulink\JCBL_Buck_Verify';

% 读取模型文件
load_system(model_path)

%% 基于最优设计参数进行仿真
fprintf('开始基于最优设计参数进行仿真...\n');

% 从最优设计数据中提取参数（基于parameter-value格式）
if height(optimal_data) > 0
    try
        % 初始化参数为默认值
        f_optimal = 500e3;
        L_optimal = 1.5e-6;
        C_optimal = 9e-6;
        Ron_optimal = 0.05;
        RL_optimal = 0.05;
        RC_optimal = 0.1;
        
        % 遍历数据行，根据parameter列的值提取对应参数
        for i = 1:height(optimal_data)
            param_name = char(optimal_data{i, 1});  % 第一列：参数名，转换为字符
            param_value = optimal_data{i, 2}; % 第二列：参数值
            
            switch param_name
                case 'f(Hz)'
                    f_optimal = param_value;
                case 'L(H)'
                    L_optimal = param_value;
                case 'C(F)'
                    C_optimal = param_value;
                case 'Ron'
                    Ron_optimal = param_value;
                case 'RL'
                    RL_optimal = param_value;
                case 'RC'
                    RC_optimal = param_value;
            end
        end
        
        fprintf('使用的最优设计参数:\n');
        fprintf('  开关频率 f: %.0f Hz\n', f_optimal);
        fprintf('  电感 L: %.2e H\n', L_optimal);
        fprintf('  电容 C: %.2e F\n', C_optimal);
        fprintf('  开关管电阻 Ron: %.3f Ω\n', Ron_optimal);
        fprintf('  电感电阻 RL: %.3f Ω\n', RL_optimal);
        fprintf('  电容电阻 RC: %.3f Ω\n', RC_optimal);
        
        % 显示优化结果
        for i = 1:height(optimal_data)
            param_name = char(optimal_data{i, 1});  % 转换为字符
            param_value = optimal_data{i, 2};
            
            switch param_name
                case 'efficiency'
                    fprintf('  预测效率: %.2f%%\n', param_value * 100);
                case 'ripple'
                    fprintf('  预测纹波系数: %.4f\n', param_value);
            end
        end
        
    catch ME
        fprintf('参数提取失败，使用默认参数: %s\n', ME.message);
        % 使用默认参数
        f_optimal = 500e3;
        L_optimal = 1.5e-6;
        C_optimal = 9e-6;
        Ron_optimal = 0.05;
        RL_optimal = 0.05;
        RC_optimal = 0.1;
    end
else
    fprintf('最优设计数据为空，使用默认参数\n');
    f_optimal = 500e3;
    L_optimal = 1.5e-6;
    C_optimal = 9e-6;
    Ron_optimal = 0.05;
    RL_optimal = 0.05;
    RC_optimal = 0.1;
end

for batch = 1:num_batches
    
    % 设置初始和结束数据标志
    start_idx = (batch-1)*n + 1;
    end_idx = min(batch*n, sum);

    % 针对simIn内存预分配个数
    num = end_idx - start_idx + 1;   

    % 内存预分配,使用repmat连续初始化n次
    simIn = repmat(Simulink.SimulationInput(model_path), 1, num);

    % 转置恢复为行向量
    Vo = Vo';
    Psw1 = Psw1';
    Psw2 = Psw2';
    Prl = Prl';
    Prc = Prc';
    Pin = Pin';
    Po = Po';
    f_record = f_record';
    L_record = L_record';
    C_record = C_record';
    Ron_record = Ron_record';
    RL_record = RL_record';
    RC_record = RC_record';
    Vo_Ripple_record = Vo_Ripple_record';
    Vo_Ripple_factor_record = Vo_Ripple_factor_record';
    Eff = Eff';

    for i = start_idx : end_idx
        
        num = i - (batch - 1) * n;    % 针对simIn函数配置次数

        % 使用最优设计参数而不是随机生成
        f_record(i) = f_optimal;
        L_record(i) = L_optimal;
        C_record(i) = C_optimal;
        Ron_record(i) = Ron_optimal;
        RL_record(i) = RL_optimal;
        RC_record(i) = RC_optimal;

        % 设置Simulink模型变量
        simIn(num) = simIn(num).setVariable('L', L_record(i));
        simIn(num) = simIn(num).setVariable('C', C_record(i));
        simIn(num) = simIn(num).setVariable('Ron', Ron_record(i));
        simIn(num) = simIn(num).setVariable('RL', RL_record(i));
        simIn(num) = simIn(num).setVariable('RC', RC_record(i));

    end

    fprintf('正在运行仿真...\n');
    simOut = sim(simIn);    % 运行仿真

    % 记录数据
    for i = start_idx : end_idx

        num = i - (batch - 1) * n;    % 针对simOut函数配置次数

        Vo(i) = simOut(1,num).vo(end,end);
        Pin(i) = simOut(1,num).pin(end,end);
        Po(i) = simOut(1,num).po(end,end);
        Psw1(i) = simOut(1,num).psw1(end,end);
        Psw2(i) = simOut(1,num).psw2(end,end);
        Prl(i) = simOut(1,num).prl(end,end);
        Prc(i) = simOut(1,num).prc(end,end);
        Vo_Ripple_record(i) = simOut(1,num).v_ripple(end,end);
        Vo_Ripple_factor_record(i) = simOut(1,num).v_ripple_factor(end,end);
        Eff(i) = Po(i) / Pin(i);

    end

    % 导出数据，矩阵转置
    Vo = Vo';
    Psw1 = Psw1';
    Psw2 = Psw2';
    Prl = Prl';
    Prc = Prc';
    Pin = Pin';
    Po = Po';
    f_record = f_record';
    L_record = L_record';
    C_record = C_record';
    Ron_record = Ron_record';
    RL_record = RL_record';
    RC_record = RC_record';
    Vo_Ripple_record = Vo_Ripple_record';
    Vo_Ripple_factor_record = Vo_Ripple_factor_record';
    Eff = Eff';

    % 创建带列名的表格
    data_table = table(Vo, f_record, L_record, C_record, Ron_record, RL_record, RC_record, Psw1, Psw2, Prl, Prc, Pin, Po, Vo_Ripple_record, Vo_Ripple_factor_record, Eff, 'VariableNames', {'Uo(V)', 'f(Hz)', 'L(H)', 'C(F)', 'Ron', 'RL', 'RC', 'Psw1(W)', 'Psw2(W)', 'Prl(W)', 'Prc(W)', 'Pin(W)', 'Po(W)', 'Vo_Ripple(V)', 'Vo_Ripple_factor', 'Efficiency'});
    
    % 保存仿真结果
    result_path = 'E:\AI-based optimized design\Data\Input_Data\optimal_simulation_result.csv';
    writetable(data_table, result_path);
    fprintf('最优设计仿真结果已保存到: %s\n', result_path);
    
    % 显示仿真结果摘要
    fprintf('\n=== 最优设计仿真结果摘要 ===\n');
    fprintf('输出电压: %.3f V\n', Vo(1));
    fprintf('输入功率: %.3f W\n', Pin(1));
    fprintf('输出功率: %.3f W\n', Po(1));
    fprintf('效率: %.2f%%\n', Eff(1)*100);
    fprintf('纹波电压: %.6f V\n', Vo_Ripple_record(1));
    fprintf('纹波系数: %.4f\n', Vo_Ripple_factor_record(1));
    fprintf('开关损耗1: %.3f W\n', Psw1(1));
    fprintf('开关损耗2: %.3f W\n', Psw2(1));
    fprintf('电感损耗: %.3f W\n', Prl(1));
    fprintf('电容损耗: %.3f W\n', Prc(1));
    fprintf('============================\n');

end

% 完成通知
fprintf('\n基于最优设计参数的仿真验证完成\n');

%% 关闭模型
% close_system(model_path, 0);