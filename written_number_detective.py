import numpy as np
import scipy.special

class NeuralNetwork:
    def __init__(self):
        # 初始化网络结构和参数
        self.input_nodes = 784
        self.hidden_nodes = 200
        self.output_nodes = 10
        self.lr = 0.1

        # 加载已训练的权重
        self.wih = np.load('wih.npy')
        self.who = np.load('who.npy')

        # 激活函数
        self.activation_function = lambda x: scipy.special.expit(x)

    def query(self, inputs_list):
        # 转换输入列表为二维数组
        inputs = np.array(inputs_list, ndmin=2).T

        # 计算隐藏层输入和输出
        hidden_inputs = np.dot(self.wih, inputs)
        hidden_outputs = self.activation_function(hidden_inputs)

        # 计算最终输出层的输入和输出
        final_inputs = np.dot(self.who, hidden_outputs)
        final_outputs = self.activation_function(final_inputs)

        # 返回结果
        return final_outputs

    def predict(self, inputs_list):
        outputs = self.query(inputs_list)
        label = np.argmax(outputs)
        return label

# 实例化神经网络
nn = NeuralNetwork()
