import numpy as np

class NeuralNetwork:
    def __init__(self, x, y):
        self.input = np.zeros(x)

        # Inputs -> Hidden Layer 1
        # self.weights1 = np.zeros((self.input.shape[1], 6))

        # FOR Values 0 -> 1
        self.weights1 = np.random.rand(self.input.shape[1], 6)

        # FOR Values -1 -> 1
        # self.weights1 = np.random.uniform(-1, 1, (self.input.shape[1], 6))

        # Hidden Layer 1 -> Hidden Layer 2
        # self.weights2 = np.zeros((self.weights1.shape[1], 6))
        self.weights2 = np.random.rand(self.weights1.shape[1], 6)

        #Hidden Layer 2 -> Outputs
        # self.weights3 = np.zeros((self.weights2.shape[1], y[0]))
        self.weights3 = np.random.rand(self.weights2.shape[1], y)

        self.output = np.zeros((y, 3))

    def inject_inputs(self, inputs):
        self.input = inputs * 0.01

    def summation_forward(self):
        self.hl1 = activation_relu_hl(np.dot(self.input, self.weights1))
        self.hl2 = activation_relu_hl(np.dot(self.hl1, self.weights2))

    def get_info(self):
        print(self.input)
        print(self.input.shape)

        print(self.weights1)
        print(self.weights1.shape)

        print(self.weights2)
        print(self.weights2.shape)

        print(self.weights3)
        print(self.weights3.shape)

        print(self.output)
        print(self.output.shape)

def activation_relu_hl(summation_output):
    if summation_output > 0:
        return summation_output
    else:
        return 0.0