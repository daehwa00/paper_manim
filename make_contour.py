import numpy as np
import matplotlib.pyplot as plt


# 가우시안 분포를 생성하는 함수
def generate_gaussian(x, y, mean, covariance):
    xy = np.stack([x.flatten(), y.flatten()]).T
    inv_cov = np.linalg.inv(covariance)
    n = mean.shape[0]
    diff = xy - mean
    exp_term = np.einsum("...k,kl,...l->...", diff, inv_cov, diff)
    return np.exp(-0.5 * exp_term).reshape(x.shape)


# 플롯의 크기와 해상도 설정
x, y = np.meshgrid(np.linspace(-5, 5, 100), np.linspace(-5, 5, 100))

# 여러 가우시안 분포의 평균과 공분산 정의
gaussians = [
    (np.array([0, 0]), np.array([[1, 0], [0, 1]])),
    (np.array([2, 2]), np.array([[0.5, 0.3], [0.3, 0.5]])),
    (np.array([-2, -1]), np.array([[0.5, 0], [0, 0.5]])),
    (np.array([1, -3]), np.array([[0.3, -0.1], [-0.1, 0.3]])),
    (np.array([-3, 2]), np.array([[0.4, 0.3], [0.3, 0.4]])),
    # 추가된 가우시안 분포들
    (np.array([3, -2]), np.array([[0.2, 0], [0, 0.2]])),
    (np.array([-2, 3]), np.array([[0.3, 0.2], [0.2, 0.3]])),
    (np.array([0, 3]), np.array([[0.4, -0.1], [-0.1, 0.4]])),
    (np.array([-3, -3]), np.array([[0.5, 0.1], [0.1, 0.5]])),
    (np.array([3, 3]), np.array([[0.3, 0], [0, 0.3]])),
    (np.array([-1, 4]), np.array([[0.4, 0.2], [0.2, 0.4]])),
    (np.array([4, -1]), np.array([[0.6, -0.2], [-0.2, 0.6]])),
    (np.array([-4, -4]), np.array([[0.3, 0.1], [0.1, 0.3]])),
    (np.array([4, 4]), np.array([[0.5, -0.1], [-0.1, 0.5]])),
]

# 가우시안 분포의 합을 계산하여 지자기 맵 표현
magnetic_map = np.zeros(x.shape)
for mean, covariance in gaussians:
    magnetic_map += generate_gaussian(x, y, mean, covariance)

# 등고선 플롯으로 지자기 맵 표현
plt.figure(figsize=(5, 5))
plt.contourf(x, y, magnetic_map, levels=20, cmap="viridis")
plt.axis("off")
plt.gca().set_position([0, 0, 1, 1])
plt.gca().set_axis_off()
plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
plt.margins(0, 0)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.savefig("magnetic_map.png")
