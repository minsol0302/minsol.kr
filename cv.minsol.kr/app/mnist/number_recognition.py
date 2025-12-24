# 머신러닝 학습의 Hello World 와 같은 MNIST(손글씨 숫자 인식) 문제를 신경망으로 풀어봅니다.
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

#########
# 신경망 모델 구성
######
class MNISTNet(nn.Module):
    def __init__(self):
        super(MNISTNet, self).__init__()
        # 784(입력 특성값) -> 256 (히든레이어 뉴런 갯수) -> 256 (히든레이어 뉴런 갯수) -> 10 (결과값 0~9 분류)
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 10)
        self.relu = nn.ReLU()
        
        # 가중치 초기화 (stddev=0.01에 해당)
        nn.init.normal_(self.fc1.weight, std=0.01)
        nn.init.normal_(self.fc2.weight, std=0.01)
        nn.init.normal_(self.fc3.weight, std=0.01)
    
    def forward(self, x):
        # 입력값을 평탄화 (28x28 -> 784)
        x = x.view(-1, 784)
        # 입력값에 가중치를 곱하고 ReLU 함수를 이용하여 레이어를 만듭니다.
        x = self.relu(self.fc1(x))
        # L1 레이어의 출력값에 가중치를 곱하고 ReLU 함수를 이용하여 레이어를 만듭니다.
        x = self.relu(self.fc2(x))
        # 최종 모델의 출력값은 fc3를 통해 10개의 분류를 가지게 됩니다.
        x = self.fc3(x)
        return x


def train_model():
    # 텐서플로우에 기본 내장된 mnist 모듈을 이용하여 데이터를 로드합니다.
    # 지정한 폴더에 MNIST 데이터가 없는 경우 자동으로 데이터를 다운로드합니다.
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))  # MNIST 데이터셋의 평균과 표준편차
    ])
    
    # 학습 데이터 로드
    train_dataset = datasets.MNIST(
        root='./mnist/data/',
        train=True,
        download=True,
        transform=transform
    )
    
    # 테스트 데이터 로드
    test_dataset = datasets.MNIST(
        root='./mnist/data/',
        train=False,
        download=True,
        transform=transform
    )
    
    # 데이터 로더 생성
    batch_size = 100
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    # 모델 생성
    model = MNISTNet()
    
    # 손실 함수 및 옵티마이저 설정
    criterion = nn.CrossEntropyLoss()  # softmax_cross_entropy_with_logits_v2에 해당
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    #########
    # 신경망 모델 학습
    ######
    num_epochs = 15
    
    for epoch in range(num_epochs):
        model.train()
        total_cost = 0
        total_batch = len(train_loader)
        
        for batch_xs, batch_ys in train_loader:
            # 옵티마이저 초기화
            optimizer.zero_grad()
            
            # 순전파
            outputs = model(batch_xs)
            loss = criterion(outputs, batch_ys)
            
            # 역전파 및 최적화
            loss.backward()
            optimizer.step()
            
            total_cost += loss.item()
        
        print('Epoch:', '%04d' % (epoch + 1),
              'Avg. cost =', '{:.3f}'.format(total_cost / total_batch))
    
    print('최적화 완료!')
    
    #########
    # 결과 확인
    ######
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for images, labels in test_loader:
            outputs = model(images)
            # model 로 예측한 값과 실제 레이블인 labels의 값을 비교합니다.
            # torch.argmax 함수를 이용해 예측한 값에서 가장 큰 값을 예측한 레이블이라고 평가합니다.
            # 예) [0.1 0 0 0.7 0 0.2 0 0 0 0] -> 3
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    print('정확도:', '{:.2f}%'.format(accuracy))


if __name__ == '__main__':
    train_model()

