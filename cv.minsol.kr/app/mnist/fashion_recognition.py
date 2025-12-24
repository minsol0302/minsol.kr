import os
# OpenMP 라이브러리 중복 초기화 오류 해결
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np


class MnistTest:
    def __init__(self):
        self.class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                           'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']
    
    def create_model(self):
        # Fashion-MNIST 데이터셋 로드
        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.5,), (0.5,))  # -1 ~ 1 범위로 정규화 (0~255 -> 0~1 -> -1~1)
        ])
        
        train_dataset = datasets.FashionMNIST(
            root='./mnist/data/',
            train=True,
            download=True,
            transform=transform
        )
        
        test_dataset = datasets.FashionMNIST(
            root='./mnist/data/',
            train=False,
            download=True,
            transform=transform
        )
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
        
        # 데이터를 numpy 배열로 변환 (시각화용)
        # PyTorch FashionMNIST의 .data는 PIL Image이므로 numpy로 변환
        train_images = np.array([np.array(img) for img in train_dataset.data]) / 255.0
        train_labels = train_dataset.targets.numpy() if hasattr(train_dataset.targets, 'numpy') else np.array(train_dataset.targets)
        test_images = np.array([np.array(img) for img in test_dataset.data]) / 255.0
        test_labels = test_dataset.targets.numpy() if hasattr(test_dataset.targets, 'numpy') else np.array(test_dataset.targets)
        
        # print('행: %d, 열: %d' % (train_images.shape[0], train_images.shape[1]))
        # print('행: %d, 열: %d' % (test_images.shape[0], test_images.shape[1]))
        
        # plt.figure()
        # plt.imshow(train_images[3])
        # plt.colorbar()
        # plt.grid(False)
        # plt.show()
        
        # 시각화 (25개 이미지)
        plt.figure(figsize=(10, 10))
        for i in range(25):
            plt.subplot(5, 5, i + 1)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            plt.imshow(train_images[i], cmap=plt.cm.binary)
            plt.xlabel(self.class_names[train_labels[i]])
        # plt.show()
        
        # 모델 정의
        """
        relu ( Rectified Linear Unit 정류한 선형 유닛)
        미분 가능한 0과 1사이의 값을 갖도록 하는 알고리즘
        softmax
        nn (neural network )의 최상위층에서 사용되며 classification 을 위한 function
        결과를 확률값으로 해석하기 위한 알고리즘
        """
        model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(28 * 28, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
            # softmax는 CrossEntropyLoss에서 자동으로 처리되므로 마지막 레이어에는 포함하지 않음
        )
        
        # 손실 함수 및 옵티마이저 설정
        criterion = nn.CrossEntropyLoss()  # sparse_categorical_crossentropy에 해당
        optimizer = optim.Adam(model.parameters())
        
        # 학습
        num_epochs = 5
        model.train()
        for epoch in range(num_epochs):
            running_loss = 0.0
            correct = 0
            total = 0
            
            for images, labels in train_loader:
                optimizer.zero_grad()
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            
            print(f'Epoch {epoch + 1}/{num_epochs}, Loss: {running_loss / len(train_loader):.4f}, Accuracy: {100 * correct / total:.2f}%')
        
        # 테스트
        model.eval()
        test_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in test_loader:
                outputs = model(images)
                loss = criterion(outputs, labels)
                test_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        test_acc = correct / total
        print('\n 테스트 정확도: ', test_acc)
        
        # 예측
        model.eval()
        all_predictions = []
        with torch.no_grad():
            for images, _ in test_loader:
                outputs = model(images)
                # softmax 적용하여 확률값으로 변환
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                all_predictions.append(probabilities.numpy())
        
        predictions = np.concatenate(all_predictions, axis=0)
        print(predictions[3])
        
        # 10개 클래스에 대한 예측을 그래프화
        arr = [predictions, test_labels, test_images]
        return arr
    
    def plot_image(self, i, predictions_array, true_label, img):
        print(' === plot_image 로 진입 ===')
        predictions_array, true_label, img = predictions_array[i], true_label[i], img[i]
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])
        
        plt.imshow(img, cmap=plt.cm.binary)
        # plt.show()
        predicted_label = np.argmax(predictions_array)
        if predicted_label == true_label:
            color = 'blue'
        else:
            color = 'red'
        
        plt.xlabel("{} {:2.0f}% ({})".format(self.class_names[predicted_label],
                                              100 * np.max(predictions_array),
                                              self.class_names[true_label]),
                   color=color)
    
    @staticmethod
    def plot_value_array(i, predictions_array, true_label):
        predictions_array, true_label = predictions_array[i], true_label[i]
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])
        thisplot = plt.bar(range(10), predictions_array, color="#777777")
        plt.ylim([0, 1])
        predicted_label = np.argmax(predictions_array)
        
        thisplot[predicted_label].set_color('red')
        thisplot[true_label].set_color('blue')


if __name__ == '__main__':
    mnist_test = MnistTest()
    arr = mnist_test.create_model()

