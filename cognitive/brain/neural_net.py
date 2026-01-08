import numpy as np
import json
import os

class NeuralNet:
    """
    A simple Multi-Layer Perceptron (MLP) built from scratch.
    Capable of learning patterns (State -> Next State) or (State -> Value).
    """
    def __init__(self, input_size, hidden_size, output_size, learning_rate=0.01):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lr = learning_rate
        
        # Initialize weights and biases (Xavier initialization)
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(1 / input_size)
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(1 / hidden_size)
        self.b2 = np.zeros((1, output_size))
        
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    
    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        """
        Forward propagation.
        """
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2) # Output layer (assuming normalized outputs)
        return self.a2

    def train(self, X, y):
        """
        Backpropagation training step.
        """
        # Forward
        output = self.forward(X)
        
        # Calculate Error
        error = y - output
        
        # Backward
        d_output = error * self.sigmoid_derivative(output)
        error_hidden = d_output.dot(self.W2.T)
        d_hidden = error_hidden * self.sigmoid_derivative(self.a1)
        
        # Update Weights
        self.W2 += self.a1.T.dot(d_output) * self.lr
        self.b2 += np.sum(d_output, axis=0, keepdims=True) * self.lr
        self.W1 += X.T.dot(d_hidden) * self.lr
        self.b1 += np.sum(d_hidden, axis=0, keepdims=True) * self.lr
        
        return np.mean(np.abs(error))

    def save(self, path):
        """Save weights to JSON (portable)"""
        data = {
            "W1": self.W1.tolist(),
            "b1": self.b1.tolist(),
            "W2": self.W2.tolist(),
            "b2": self.b2.tolist()
        }
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def load(self, path):
        if not os.path.exists(path): return
        with open(path, "r") as f:
            data = json.load(f)
            self.W1 = np.array(data["W1"])
            self.b1 = np.array(data["b1"])
            self.W2 = np.array(data["W2"])
            self.b2 = np.array(data["b2"])
